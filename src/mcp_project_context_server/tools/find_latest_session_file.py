"""Tool: find_latest_session_file — deterministic lookup of the newest session file."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import list_context_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``find_latest_session_file`` tool call.

    :param arguments: (dict) Tool input dict. Requires key ``"project_path"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        naming the most recent ``sessions/*.md`` file (sorted by filename), or
        "No session files found." when none exist.
    """
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    session_files = await list_context_files(_project_path, prefix="sessions/")
    if not session_files:
        return [types.TextContent(type="text", text="No session files found.")]

    return [types.TextContent(type="text", text=f"Latest session file: {session_files[-1]}")]
