"""Tool: list_adr_sections — list an ADR's top-level section names in order."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.adr import resolve_adr
from mcp_project_context_server.helpers.sections import split_sections
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``list_adr_sections`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"number_or_filename"``.
    :return: (list) A single :class:`~mcp.types.TextContent` item containing the
        ADR's top-level (``##``) section names in document order, or a
        not-found error message.
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

    sections = split_sections(resolution.content)
    names = [section.name for section in sections if section.name]
    if not names:
        text = f"ADR-{resolution.info.number:05d} ({resolution.info.filename}) has no top-level (##) sections."
    else:
        text = f"Sections in ADR-{resolution.info.number:05d} ({resolution.info.filename}):\n" + "\n".join(
            f"- {name}" for name in names
        )

    return [types.TextContent(type="text", text=text)]
