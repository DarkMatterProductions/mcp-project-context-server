"""Tool: save_session_summary — writes a session summary to .context/sessions/."""

import os
from datetime import datetime

from mcp import types

from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access


async def handle(arguments: dict) -> list[types.TextContent]:
    summary: str = arguments["summary"]

    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    resolved_path, is_remote = resolve_project_path(_project_path)

    if is_remote:
        return await _handle_remote(resolved_path, summary)

    context_dir = find_context_dir(resolved_path)
    if not context_dir:
        return [
            types.TextContent(
                type="text",
                text=f"No .context/ directory found near {arguments['project_path']}",
            )
        ]

    sessions_dir = context_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    session_file = sessions_dir / f"{today}.md"

    if session_file.exists():
        timestamp = datetime.now().strftime("%H:%M")
        file_content = f"{session_file.read_text(encoding='utf-8')}" f"\n\n### Session at {timestamp}\n\n{summary}"
    else:
        file_content = f"# Session: {today}\n\n{summary}"

    session_file.write_text(file_content, encoding="utf-8")
    # as_posix() gives a consistent forward-slash path regardless of platform.
    return [
        types.TextContent(
            type="text",
            text=f"Session summary saved to {session_file.as_posix()}",
        )
    ]


async def _handle_remote(repo_id: str, summary: str) -> list[types.TextContent]:
    """Save a session summary to a remote repository's ``.context/sessions/``.

    Write target is configurable via ``REPO_SESSION_WRITE_MODE``:

    * ``"direct"`` (default) — write straight to ``REPO_SESSION_BRANCH`` if
      set, otherwise the repository's default branch.
    * ``"branch"`` — create a new branch (``mcp-session/{date}-{HHMMSS}``)
      off the default branch and write there, leaving the target branch
      untouched for review.
    """
    provider = get_repository_provider()

    today = datetime.now().strftime("%Y-%m-%d")
    session_key = f"sessions/{today}.md"
    target_path = f".context/{session_key}"

    try:
        files = await provider.fetch_context_files(repo_id)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=f"Error accessing repository: {exc}")]

    existing = files.get(session_key)
    if existing:
        timestamp = datetime.now().strftime("%H:%M")
        file_content = f"{existing}\n\n### Session at {timestamp}\n\n{summary}"
    else:
        file_content = f"# Session: {today}\n\n{summary}"

    message = f"Add session summary for {today}"
    write_mode = os.getenv("REPO_SESSION_WRITE_MODE", "direct").strip().lower()

    try:
        if write_mode == "branch":
            branch_name = f"mcp-session/{today}-{datetime.now().strftime('%H%M%S')}"
            await provider.create_branch(repo_id, branch_name)
            await provider.write_file(repo_id, target_path, file_content, message, branch=branch_name)
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"Session summary pushed to new branch `{branch_name}` on `{repo_id}` "
                        f"(provider: {provider.provider_name}). Path: {target_path}"
                    ),
                )
            ]

        target_branch = os.getenv("REPO_SESSION_BRANCH") or None
        await provider.write_file(repo_id, target_path, file_content, message, branch=target_branch)
        branch_label = target_branch or await provider.get_default_branch(repo_id)
        return [
            types.TextContent(
                type="text",
                text=(
                    f"Session summary saved to `{repo_id}` ({target_path}) on branch "
                    f"`{branch_label}` (provider: {provider.provider_name})."
                ),
            )
        ]
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=f"Error saving session summary: {exc}")]
