"""Tool: index_project_context — re-indexes .context/ into the configured vector store."""
import logging
import os

from mcp import types

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access
from mcp_project_context_server.integrations.vectorstore.registry import get_indexer

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``index_project_context`` tool call.

    :param arguments: (dict) Tool input dict. Requires key ``"project_path"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with the indexing result summary or an error message.
    """
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    indexer = get_indexer()
    result = await indexer(_project_path)
    return [types.TextContent(type="text", text=result)]
