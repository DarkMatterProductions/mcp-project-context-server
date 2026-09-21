"""Tool: read_adr_status — read one ADR's parsed status and title."""

import logging
import os

from mcp import types

from mcp_project_context_server.helpers.adr import parse_status, resolve_adr
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``read_adr_status`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"number_or_filename"``.
    :return: (list) A single :class:`~mcp.types.TextContent` item containing the
        ADR's title and parsed status, an explicit "legacy format" message for
        ADRs that don't use the standard ``## Status`` heading, or a not-found
        error message.
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

    status, found = parse_status(content)
    if not found:
        return [
            types.TextContent(
                type="text",
                text=(
                    f"ADR-{info.number:05d} ({info.filename}) uses the legacy "
                    "`**Status:**` inline format, which is not supported by this tool. "
                    "Read the file directly (e.g. via `read_adr`) to determine its status."
                ),
            )
        ]

    return [
        types.TextContent(
            type="text",
            text=f"ADR-{info.number:05d}: {info.title}\nStatus: {status if status else 'Unknown'}",
        )
    ]
