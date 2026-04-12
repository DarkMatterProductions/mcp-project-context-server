"""Tool: load_project_context — loads project.md, ADRs, and last session."""

from mcp import types
from mcp_project_context_server.helpers.context import find_context_dir


async def handle(arguments: dict) -> list[types.TextContent]:
    context_dir = find_context_dir(arguments["project_path"])
    if not context_dir:
        return [types.TextContent(
            type="text",
            text=f"No .context/ directory found near {arguments['project_path']}",
        )]

    parts: list[str] = []

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