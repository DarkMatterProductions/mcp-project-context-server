"""Tool: load_context_files — load specific .context/ files, tagged with path + SHA-512."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import format_tagged_file, hash_content, resolve_requested_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``load_context_files`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"`` and
        ``"files"`` (a list of ``.context/``-relative paths to load).
    :return: (list) One :class:`~mcp.types.TextContent` block per requested file —
        a ``<context-file path="..." sha512="...">`` tagged block for files that
        were found, or a "File not found" message for files that were not.
    """
    files: list[str] = arguments["files"]
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    found, _missing = await resolve_requested_files(_project_path, files)

    blocks: list[types.TextContent] = []
    for path in files:
        if path in found:
            content = found[path]
            blocks.append(types.TextContent(type="text", text=format_tagged_file(path, hash_content(content), content)))
        else:
            blocks.append(types.TextContent(type="text", text=f"File not found: {path}"))

    return blocks
