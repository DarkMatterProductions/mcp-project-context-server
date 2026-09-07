"""Tool: search_adr_sections — semantic search scoped to a single resolved ADR."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.adr import resolve_adr
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access
from mcp_project_context_server.tools.search_shared import run_search

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> types.CallToolResult:
    """Handle the ``search_adr_sections`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``,
        ``"number_or_filename"``, and ``"query"``; optional ``"n_results"``
        (defaults to 5).
    :return: (CallToolResult) The unstructured text (matching chunks from the
        resolved ADR, each labeled with its section) alongside a
        ``structured_content`` object of the shape
        ``{"results": [{"file", "chunk", "content", "distance", "section"}, ...]}``,
        or an error/"not found" ``CallToolResult`` if the ADR can't be resolved.
    """
    number_or_filename = arguments["number_or_filename"]
    query = arguments["query"]
    n_results = arguments.get("n_results", 5)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=str(exc))],
            structured_content={"results": []},
        )

    resolution = await resolve_adr(_project_path, number_or_filename)
    if resolution.error:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=resolution.error)],
            structured_content={"results": []},
        )

    return await run_search(_project_path, query, n_results, exact_file=resolution.info.path)
