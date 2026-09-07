"""Tool: update_adr_status — transition an ADR's Status, with lifecycle guardrails."""
import logging
import os
import re
from datetime import datetime

from mcp import types

from mcp_project_context_server.helpers.adr import find_section, list_adrs, parse_status, replace_section, resolve_adr
from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.helpers.repo_write import append_reindex_note, write_context_file
from mcp_project_context_server.helpers.sections import Section, split_sections
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access

logger = logging.getLogger(__name__)

_LIFECYCLE_ORDER = ["Proposed", "Under Review", "Accepted", "Implemented", "Deprecated"]
_SUPERSEDED_RE = re.compile(r"^Superseded by (ADR-(\d{5}))$")
_PLACEHOLDER_BODIES = {"", "[Pending review]", "[Pending Review]"}


def _section_body(section: Section) -> str:
    """Return *section*'s content without its heading line, stripped."""
    lines = section.content.splitlines()
    return "\n".join(lines[1:]).strip()


def _remove_section(content: str, section_name: str) -> str:
    """Return *content* with the top-level section named *section_name* removed entirely."""
    return "".join(section.content for section in split_sections(content) if section.name != section_name)


def _append_review_discussion(content: str, explanation: str) -> str:
    """Append a timestamped entry to the ``ADR Review Discussion`` section, if present."""
    section = find_section(content, "ADR Review Discussion")
    if section is None:
        return content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"**[{timestamp}] [update_adr_status]:** {explanation.strip()}"
    body = _section_body(section)
    new_body = entry if body in _PLACEHOLDER_BODIES else f"{body}\n\n{entry}"
    return replace_section(content, "ADR Review Discussion", new_body)


def _classify_transition(current_status: str, new_status: str) -> str:
    """Classify a status transition as ``"no-op"``, ``"normal"``, or ``"unusual"``.

    ``"normal"`` is exactly one forward step through the standard lifecycle
    (Proposed -> Under Review -> Accepted -> Implemented -> Deprecated).
    Anything else — backward moves, skipped steps, or transitioning to
    ``Superseded by ADR-XXXXX`` — is ``"unusual"`` and requires an explanation.
    """
    if current_status == new_status:
        return "no-op"
    if current_status in _LIFECYCLE_ORDER and new_status in _LIFECYCLE_ORDER:
        if _LIFECYCLE_ORDER.index(new_status) == _LIFECYCLE_ORDER.index(current_status) + 1:
            return "normal"
    return "unusual"


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``update_adr_status`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``,
        ``"number_or_filename"``, and ``"new_status"`` (one of the standard
        lifecycle values, or ``"Superseded by ADR-XXXXX"`` where the target ADR
        must already exist). Optional ``"explanation"`` (str) — required for
        "unusual" transitions and for transitioning to ``Accepted`` when the
        ``Decision`` section is still a placeholder; when the ADR is currently
        ``Proposed``/``Under Review``, it is also appended as a timestamped
        entry to ``ADR Review Discussion`` before any other mutation. Optional
        ``"auto_reindex"`` (bool, default False).
    :return: (list) A single :class:`~mcp.types.TextContent` item confirming the
        write (and either the re-index result or a manual-reindex reminder), a
        no-op notice, or an error message.
    """
    number_or_filename = arguments["number_or_filename"]
    new_status = arguments["new_status"].strip()
    explanation = arguments.get("explanation")
    auto_reindex = arguments.get("auto_reindex", False)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    superseded_match = _SUPERSEDED_RE.match(new_status)
    if new_status not in _LIFECYCLE_ORDER and not superseded_match:
        return [
            types.TextContent(
                type="text",
                text=(
                    f"Invalid status '{new_status}'. Must be one of: {', '.join(_LIFECYCLE_ORDER)}, "
                    "or 'Superseded by ADR-XXXXX'."
                ),
            )
        ]

    all_adrs, _warnings = await list_adrs(_project_path)
    if superseded_match:
        target_number = int(superseded_match.group(2))
        if not any(info.number == target_number for info in all_adrs):
            return [
                types.TextContent(
                    type="text",
                    text=f"Cannot set status to '{new_status}': ADR-{target_number:05d} does not exist.",
                )
            ]

    resolution = await resolve_adr(_project_path, number_or_filename)
    if resolution.error:
        return [types.TextContent(type="text", text=resolution.error)]

    current_status, found = parse_status(resolution.content)
    if not found:
        return [
            types.TextContent(
                type="text",
                text=(
                    f"ADR-{resolution.info.number:05d} ({resolution.info.filename}) uses the legacy "
                    "`**Status:**` inline format, which is not supported by this tool."
                ),
            )
        ]

    transition = _classify_transition(current_status, new_status)
    if transition == "no-op":
        return [
            types.TextContent(
                type="text",
                text=f"ADR-{resolution.info.number:05d} is already '{current_status}'. No changes made.",
            )
        ]
    if transition == "unusual" and not explanation:
        return [
            types.TextContent(
                type="text",
                text=(
                    f"Transitioning ADR-{resolution.info.number:05d} from '{current_status}' to "
                    f"'{new_status}' is unusual and requires an 'explanation' argument describing why."
                ),
            )
        ]

    content = resolution.content

    if current_status in ("Proposed", "Under Review") and explanation:
        content = _append_review_discussion(content, explanation)

    if new_status == "Accepted":
        decision_section = find_section(content, "Decision")
        decision_body = _section_body(decision_section) if decision_section else ""
        if decision_body in _PLACEHOLDER_BODIES:
            if not explanation:
                return [
                    types.TextContent(
                        type="text",
                        text=(
                            f"Transitioning ADR-{resolution.info.number:05d} to 'Accepted' requires a "
                            "populated Decision section. Provide 'explanation' with the decision "
                            "rationale, or populate Decision via edit_adr first."
                        ),
                    )
                ]
            content = replace_section(content, "Decision", explanation.strip())
        content = _remove_section(content, "ADR Review Discussion")

    content = replace_section(content, "Status", new_status)

    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(_project_path, provider.provider_name)
    commit_message = f"Update ADR-{resolution.info.number:05d} status: {current_status} -> {new_status}"

    if is_remote:
        message = await write_context_file(provider, resolved_path, resolution.info.path, content, commit_message)
    else:
        context_dir = find_context_dir(resolved_path)
        if context_dir is None:
            return [
                types.TextContent(
                    type="text",
                    text=f"No .context/ directory found near {arguments['project_path']}",
                )
            ]
        (context_dir / resolution.info.path).write_text(content, encoding="utf-8")
        message = f"Updated ADR-{resolution.info.number:05d} status: {current_status} -> {new_status}."

    final_text = await append_reindex_note(_project_path, message, auto_reindex)
    return [types.TextContent(type="text", text=final_text)]
