"""Tool: read_adr_section — read a single named top-level section of an ADR."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.adr import find_section, resolve_adr
from mcp_project_context_server.helpers.sections import split_sections
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``read_adr_section`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``,
        ``"number_or_filename"``, and ``"section"`` (the exact ``##`` heading
        text, without the ``##`` marker).
    :return: (list) A single :class:`~mcp.types.TextContent` item containing the
        requested section's raw content, or an error message listing the ADR's
        available section names when the requested one isn't found.
    """
    number_or_filename = arguments["number_or_filename"]
    section_name = arguments["section"]
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

    section = find_section(content, section_name)
    if section is None:
        available = [s.name for s in split_sections(content) if s.name]
        available_text = ", ".join(available) if available else "none"
        return [
            types.TextContent(
                type="text",
                text=(
                    f"No section named '{section_name}' found in ADR-{info.number:05d} "
                    f"({info.filename}). Available sections: {available_text}."
                ),
            )
        ]

    return [types.TextContent(type="text", text=section.content)]
