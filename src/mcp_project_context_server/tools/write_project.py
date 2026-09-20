"""Tool: write_project — overwrite the full content of .context/project.md."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.helpers.repo_write import append_reindex_note, write_context_file
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``write_project`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"content"`` (the full new content of ``project.md``). Optional
        ``"auto_reindex"`` (bool, default False).
    :return: (list) A single :class:`~mcp.types.TextContent` item confirming the
        write (and either the re-index result or a manual-reindex reminder), or
        an error message.
    """
    content = arguments["content"]
    auto_reindex = arguments.get("auto_reindex", False)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(_project_path, provider.provider_name)
    commit_message = "Update project.md"

    if is_remote:
        message = await write_context_file(provider, resolved_path, "project.md", content, commit_message)
    else:
        context_dir = find_context_dir(resolved_path)
        if context_dir is None:
            return [
                types.TextContent(
                    type="text",
                    text=f"No .context/ directory found near {arguments['project_path']}",
                )
            ]
        (context_dir / "project.md").write_text(content, encoding="utf-8")
        message = "Updated project.md."

    final_text = await append_reindex_note(_project_path, message, auto_reindex)
    return [types.TextContent(type="text", text=final_text)]
