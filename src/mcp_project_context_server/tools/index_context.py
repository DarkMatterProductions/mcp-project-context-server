"""Tool: index_project_context — re-indexes .context/ into the configured vector store."""

import os

from mcp import types

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access
from mcp_project_context_server.integrations.vectorstore.registry import get_indexer


async def handle(arguments: dict) -> list[types.TextContent]:
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    indexer = get_indexer()
    result = await indexer(_project_path)
    return [types.TextContent(type="text", text=result)]
