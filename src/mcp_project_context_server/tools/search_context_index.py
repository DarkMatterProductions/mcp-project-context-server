"""Tool: search_context_index — semantic search over the whole indexed context."""
import logging
import os

from mcp import types

from mcp_project_context_server.tools.search_shared import run_search

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``search_context_index`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"query"``; optional key ``"n_results"`` (defaults to 5).
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with the matching context snippets, or an error/"not found" message.
    """
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    return await run_search(_project_path, query, n_results, file_prefix=None)
