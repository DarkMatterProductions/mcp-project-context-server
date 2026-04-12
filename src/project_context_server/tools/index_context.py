"""Tool: index_project_context — re-indexes .context/ into ChromaDB."""

from mcp import types
from project_context_server.indexing.chroma.indexer import index_project_context


async def handle(arguments: dict) -> list[types.TextContent]:
    result = index_project_context(arguments["project_path"])
    return [types.TextContent(type="text", text=result)]