"""Tool: load_project_context — loads project.md, ADRs, and last session."""

import logging
import os

from mcp import types
from pathlib import Path

from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``load_project_context`` tool call.

    :param arguments: (dict) Tool input dict. Requires key ``"project_path"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with the assembled project.md, ADRs, and latest session summary, or an
        error/"not found" message.
    """
    print(Path(__file__))
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    resolved_path, is_remote = resolve_project_path(_project_path)

    if is_remote:
        try:
            provider = get_repository_provider()
            files = await provider.fetch_context_files(resolved_path)
        except RepositoryError as exc:
            return [types.TextContent(type="text", text=f"Error accessing repository: {exc}")]
        if not files:
            return [types.TextContent(type="text", text=f"No .context/ directory found in {resolved_path}")]

        parts: list[str] = []

        project_md = files.get("project.md")
        if project_md is not None:
            parts.append(f"## project.md\n\n{project_md}")

        decisions = sorted(k for k in files if k.startswith("decisions/"))
        if decisions:
            parts.append("## Architecture Decisions\n")
            for key in decisions:
                parts.append(f"### {key.rsplit('/', 1)[-1]}\n{files[key]}")

        sessions = sorted(k for k in files if k.startswith("sessions/"))
        if sessions:
            latest_key = sessions[-1]
            latest_stem = latest_key.rsplit("/", 1)[-1].removesuffix(".md")
            parts.append(f"## Last Session ({latest_stem})\n\n{files[latest_key]}")

        result = "\n\n---\n\n".join(parts)
        return [types.TextContent(type="text", text=result or "No context files found.")]

    context_dir = find_context_dir(resolved_path)
    if not context_dir:
        return [
            types.TextContent(
                type="text",
                text=f"No .context/ directory found near {arguments['project_path']}",
            )
        ]

    parts = []

    project_md = context_dir / "project.md"
    if project_md.exists():
        parts.append(f"## project.md\n\n{project_md.read_text(encoding='utf-8')}")

    decisions_dir = context_dir / "decisions"
    if decisions_dir.exists():
        adrs = sorted(decisions_dir.glob("*.md"))
        if adrs:
            parts.append("## Architecture Decisions\n")
            for adr in adrs:
                parts.append(f"### {adr.name}\n{adr.read_text(encoding='utf-8')}")

    sessions_dir = context_dir / "sessions"
    if sessions_dir.exists():
        session_files = sorted(sessions_dir.glob("*.md"))
        if session_files:
            latest = session_files[-1]
            parts.append(f"## Last Session ({latest.stem})\n\n{latest.read_text(encoding='utf-8')}")

    result = "\n\n---\n\n".join(parts)
    return [types.TextContent(type="text", text=result or "No context files found.")]
