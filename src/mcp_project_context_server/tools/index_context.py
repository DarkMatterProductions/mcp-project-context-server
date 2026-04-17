"""Tool: index_project_context — re-indexes .context/ into ChromaDB."""

import os

from mcp import types

from mcp_project_context_server.indexing.chroma.indexer import index_project_context


async def handle(arguments: dict) -> list[types.TextContent]:
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    result = await index_project_context(_project_path)
    return [types.TextContent(type="text", text=result)]
