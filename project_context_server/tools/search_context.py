"""Tool: search_project_context — semantic search over indexed context."""

from mcp import types
from project_context_server.integrations.chroma.client import chroma_client
from project_context_server.integrations.ollama.client import get_embedding
from project_context_server.helpers.context import find_context_dir, collection_name_for


async def handle(arguments: dict) -> list[types.TextContent]:
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)

    context_dir = find_context_dir(arguments["project_path"])
    if not context_dir:
        return [types.TextContent(
            type="text",
            text=f"No .context/ directory found near {arguments['project_path']}",
        )]

    col_name = collection_name_for(context_dir)

    try:
        collection = chroma_client.get_collection(col_name)
    except Exception:
        return [types.TextContent(
            type="text",
            text=f"Collection '{col_name}' not found. Run index_project_context first.",
        )]

    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
    )

    if not results["documents"][0]:
        return [types.TextContent(type="text", text="No results found.")]

    output_parts = [
        f"**[{meta['file']}]**\n{doc}"
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]
    return [types.TextContent(type="text", text="\n\n---\n\n".join(output_parts))]