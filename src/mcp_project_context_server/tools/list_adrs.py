"""Tool: list_adrs — lightweight structural listing of .context/decisions/."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.adr import list_adrs as _list_adrs
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``list_adrs`` tool call.

    :param arguments: (dict) Tool input dict. Requires key ``"project_path"``.
    :return: (list) A single :class:`~mcp.types.TextContent` item containing a
        markdown table of every well-named ADR (number, title, status, filename),
        plus a warnings block for malformed/unreadable filenames if any.
    """
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    infos, warnings = await _list_adrs(_project_path)

    if not infos:
        text = "No ADRs found in .context/decisions/."
    else:
        lines = ["| Number | Title | Status | Filename |", "|---|---|---|---|"]
        for info in infos:
            status = info.status if info.status else "_(unparsed — legacy format)_"
            title = info.title or "_(untitled)_"
            lines.append(f"| ADR-{info.number:05d} | {title} | {status} | {info.filename} |")
        text = "\n".join(lines)

    if warnings:
        text += "\n\n**Warnings:**\n" + "\n".join(f"- {warning}" for warning in warnings)

    return [types.TextContent(type="text", text=text)]
