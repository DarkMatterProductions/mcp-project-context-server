"""Tool: save_session_summary — writes a session summary to .context/sessions/."""

from datetime import datetime

from mcp import types
from mcp_project_context_server.helpers.context import find_context_dir


async def handle(arguments: dict) -> list[types.TextContent]:
    summary: str = arguments["summary"]

    context_dir = find_context_dir(arguments["project_path"])
    if not context_dir:
        return [types.TextContent(
            type="text",
            text=f"No .context/ directory found near {arguments['project_path']}",
        )]

    sessions_dir = context_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    session_file = sessions_dir / f"{today}.md"

    if session_file.exists():
        timestamp = datetime.now().strftime("%H:%M")
        file_content = (
            f"{session_file.read_text(encoding='utf-8')}"
            f"\n\n### Session at {timestamp}\n\n{summary}"
        )
    else:
        file_content = f"# Session: {today}\n\n{summary}"

    session_file.write_text(file_content, encoding="utf-8")
    # as_posix() gives a consistent forward-slash path regardless of platform.
    return [types.TextContent(
        type="text",
        text=f"Session summary saved to {session_file.as_posix()}",
    )]