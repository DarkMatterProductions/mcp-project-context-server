"""Tool: reload_active_context_file — refresh files whose on-disk content changed."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import format_tagged_file, hash_content, resolve_requested_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``reload_active_context_file`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"`` and
        ``"files"`` — a list of ``{"path": ..., "known_sha512": ...}`` entries
        describing files currently held in active context.
    :return: (list) One :class:`~mcp.types.TextContent` block per entry: "No change"
        when the current SHA-512 matches ``known_sha512``, a fresh tagged block
        plus a discard note when it differs, or "File not found" when the file
        no longer exists.
    """
    entries: list[dict] = arguments["files"]
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    paths = [entry["path"] for entry in entries]
    found, _missing = await resolve_requested_files(_project_path, paths)

    blocks: list[types.TextContent] = []
    for entry in entries:
        path = entry["path"]
        known_sha512 = entry["known_sha512"]

        if path not in found:
            blocks.append(types.TextContent(type="text", text=f"File not found: {path}"))
            continue

        content = found[path]
        current_sha512 = hash_content(content)
        if current_sha512 == known_sha512:
            blocks.append(types.TextContent(type="text", text=f"No change: {path}"))
            continue

        tagged = format_tagged_file(path, current_sha512, content)
        blocks.append(
            types.TextContent(
                type="text",
                text=f"{tagged}\n\nNote: '{path}' changed — discard the stale block previously loaded for this path.",
            )
        )

    return blocks
