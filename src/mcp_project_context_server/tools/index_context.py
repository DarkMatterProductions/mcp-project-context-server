"""Tool: index_project_context — re-indexes .context/ into the configured vector store."""

import os

from mcp import types

from mcp_project_context_server.integrations.vectorstore.registry import get_indexer


async def handle(arguments: dict) -> list[types.TextContent]:
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    index_project_context = get_indexer()
    result = await index_project_context(_project_path)
    return [types.TextContent(type="text", text=result)]
