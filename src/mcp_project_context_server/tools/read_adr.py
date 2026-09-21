"""Tool: read_adr — read one ADR's full raw content by number or filename."""

import logging
import os

from mcp import types

from mcp_project_context_server.helpers.adr import resolve_adr
from mcp_project_context_server.helpers.context_files import format_tagged_file, hash_content
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``read_adr`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"number_or_filename"``.
    :return: (list) A single :class:`~mcp.types.TextContent` item containing the
        ADR's content tagged with its path and SHA-512 hash (the same format
        used by ``load_context_files``, so ``reload_active_context_file`` keeps
        working unmodified on ADR paths), or a not-found error message.
    """
    number_or_filename = arguments["number_or_filename"]
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    resolution = await resolve_adr(_project_path, number_or_filename)
    if resolution.error:
        return [types.TextContent(type="text", text=resolution.error)]

    info = resolution.info
    content = resolution.content
    assert info is not None
    assert content is not None
    return [
        types.TextContent(
            type="text",
            text=format_tagged_file(info.path, hash_content(content), content),
        )
    ]
