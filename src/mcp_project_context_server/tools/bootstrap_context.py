"""Tool: bootstrap_context — atomically scaffold a new .context/ directory."""

import logging
import os
from importlib import resources
from pathlib import Path

from mcp import types

from mcp_project_context_server.helpers.adr import list_adrs
from mcp_project_context_server.helpers.bootstrap_templates import render_project_md
from mcp_project_context_server.helpers.context import resolve_project_path
from mcp_project_context_server.helpers.context_files import resolve_requested_files
from mcp_project_context_server.helpers.custom_bootstrap_questions import load_project_questions
from mcp_project_context_server.helpers.repo_write import append_reindex_note, write_context_file
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access
from mcp_project_context_server.tools import create_adr, write_project

logger = logging.getLogger(__name__)

_GOVERNANCE_ADR_TITLE = "Consistent Use of Architecture Decision Records in the Standard Development Cycle"
_GOVERNANCE_ADR_CONTEXT = (
    "This project's .context/ directory was bootstrapped with a standard governance process "
    "for tracking significant design decisions. Decisions that affect more than one component, "
    "have non-obvious trade-offs, would be costly to reverse, or reflect a constraint or policy "
    "must be captured as an Architecture Decision Record (ADR) following the process defined in "
    "`.context/ADR_CREATE_AND_MANAGEMENT.md`, as part of the mandatory plan-propose-approve-"
    "implement development cycle defined in `.context/PLANNING_LOOP.md`."
)

_TEMPLATE_FILENAMES = ["ADR_CREATE_AND_MANAGEMENT.md", "PLANNING_LOOP.md"]


def _read_template(filename: str) -> str:
    """Read a bundled bootstrap template's content from the installed package."""
    return resources.files("mcp_project_context_server").joinpath("templates", filename).read_text(encoding="utf-8")


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``bootstrap_context`` tool call.

    Atomically scaffolds a brand-new ``.context/`` directory: ``decisions/`` and
    ``sessions/`` directories, the two bundled governance docs
    (``ADR_CREATE_AND_MANAGEMENT.md``, ``PLANNING_LOOP.md``), an interview-driven
    ``project.md`` (via :func:`~mcp_project_context_server.tools.write_project.handle`),
    and a governance ADR-00001 establishing the ADR process (via
    :func:`~mcp_project_context_server.tools.create_adr.handle`). Every step is
    additive and idempotent — an artifact that already exists is skipped rather
    than overwritten. If the target repository has a
    ``.project-bootstrap-questions.yaml`` file at its root, its questions are
    merged into the interview set used to render ``project.md``.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"`` and
        ``"project_name"``. Optional ``"project_sections"`` (dict, string keys
        from ``get_bootstrap_questions("project")`` to answer strings, default
        ``{}``) and ``"auto_reindex"`` (bool, default False).
    :return: (list) A single :class:`~mcp.types.TextContent` item summarizing
        what was created vs. skipped for each artifact, or an error message.
    """
    project_name = arguments["project_name"].strip()
    project_sections = arguments.get("project_sections", {})
    auto_reindex = arguments.get("auto_reindex", False)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(_project_path, provider.provider_name)

    summary: list[str] = []

    if is_remote:
        summary.append(
            "- `.context/decisions/` and `.context/sessions/`: not created explicitly on remote "
            "providers (git has no empty-directory concept; `decisions/` appears once the "
            "governance ADR below is written, `sessions/` once a session summary is first saved)."
        )
    else:
        root = Path(resolved_path).resolve()
        if not root.is_dir():
            return [types.TextContent(type="text", text=f"'{arguments['project_path']}' is not an existing directory.")]
        context_dir = root / ".context"
        (context_dir / "decisions").mkdir(parents=True, exist_ok=True)
        (context_dir / "sessions").mkdir(parents=True, exist_ok=True)
        summary.append("- `.context/decisions/` and `.context/sessions/`: created (or already present).")

    for filename in _TEMPLATE_FILENAMES:
        found, _missing = await resolve_requested_files(_project_path, [filename])
        if filename in found:
            summary.append(f"- `.context/{filename}`: skipped (already exists).")
            continue
        content = _read_template(filename)
        if is_remote:
            message = await write_context_file(provider, resolved_path, filename, content, f"Bootstrap {filename}")
        else:
            (Path(resolved_path).resolve() / ".context" / filename).write_text(content, encoding="utf-8")
            message = f"Created {filename}."
        summary.append(f"- `.context/{filename}`: {message}")

    project_questions, question_warnings = await load_project_questions(_project_path)

    found, _missing = await resolve_requested_files(_project_path, ["project.md"])
    if "project.md" in found:
        summary.append("- `.context/project.md`: skipped (already exists).")
    else:
        content = render_project_md(project_name, project_sections, project_questions)
        result = await write_project.handle({"project_path": _project_path, "content": content, "auto_reindex": False})
        summary.append(f"- `.context/project.md`: {result[0].text.splitlines()[0]}")

    existing_adrs, _warnings = await list_adrs(_project_path)
    if existing_adrs:
        summary.append("- Governance ADR: skipped (an ADR already exists).")
    else:
        result = await create_adr.handle(
            {
                "project_path": _project_path,
                "title": _GOVERNANCE_ADR_TITLE,
                "context": _GOVERNANCE_ADR_CONTEXT,
                "auto_reindex": False,
            }
        )
        summary.append(f"- Governance ADR: {result[0].text.splitlines()[0]}")

    header = f"Bootstrapped .context/ for '{project_name}':"
    body = header + "\n\n" + "\n".join(summary)
    if question_warnings:
        body += "\n\n**Warnings:**\n" + "\n".join(f"- {w}" for w in question_warnings)
    final_text = await append_reindex_note(_project_path, body, auto_reindex)
    return [types.TextContent(type="text", text=final_text)]
