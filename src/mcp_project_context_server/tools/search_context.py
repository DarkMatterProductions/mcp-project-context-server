"""Tool: search_project_context — semantic search over indexed context."""

import os
from collections.abc import Sequence
from typing import cast

from mcp import types

from mcp_project_context_server.helpers.context import collection_name_for, find_context_dir
from mcp_project_context_server.integrations.chroma.client import chroma_client
from mcp_project_context_server.integrations.ollama.client import get_embedding


async def handle(arguments: dict) -> list[types.TextContent]:
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)

    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    context_dir = find_context_dir(_project_path)
    if not context_dir:
        return [
            types.TextContent(
                type="text",
                text=f"No .context/ directory found near {arguments['project_path']}",
            )
        ]

    col_name = collection_name_for(context_dir)

    try:
        collection = chroma_client.get_collection(col_name)
    except Exception:
        return [
            types.TextContent(
                type="text",
                text=f"Collection '{col_name}' not found. Run index_project_context first.",
            )
        ]

    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=cast(list[Sequence[float]], [query_embedding]),
        n_results=min(n_results, collection.count()),
    )

    docs = results["documents"]
    metas = results["metadatas"]
    if docs is None or metas is None or not docs[0]:
        return [types.TextContent(type="text", text="No results found.")]

    output_parts = [f"**[{meta['file']}]**\n{doc}" for doc, meta in zip(docs[0], metas[0])]
    return [types.TextContent(type="text", text="\n\n---\n\n".join(output_parts))]
