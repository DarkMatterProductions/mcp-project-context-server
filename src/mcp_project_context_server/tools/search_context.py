"""Tool: search_project_context — semantic search over indexed context.

Before executing a search, the tool reads the provenance metadata stored on
the collection at index time and compares it against the current provider
configuration.  If the embedding provider or model has changed, a warning is
prepended to the results so the user knows the index may need rebuilding.
"""

import os

from mcp import types

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.helpers.context import (
    collection_name_for,
    collection_name_for_repo_id,
    find_context_dir,
    resolve_project_path,
)
from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreError
from mcp_project_context_server.integrations.vectorstore.registry import get_vector_store

_MISMATCH_WARNING = (
    "⚠️  **Provider mismatch detected** — the index was built with "
    "`{old_provider}/{old_model}` but the current provider is "
    "`{new_provider}/{new_model}`.  Search results may be inaccurate.  "
    "Please re-run `index_project_context` to rebuild the index.\n\n---\n\n"
)


async def handle(arguments: dict) -> list[types.TextContent]:
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)

    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    resolved_path, is_remote = resolve_project_path(_project_path)

    if is_remote:
        col_name = collection_name_for_repo_id(resolved_path)
    else:
        context_dir = find_context_dir(resolved_path)
        if not context_dir:
            return [
                types.TextContent(
                    type="text",
                    text=f"No .context/ directory found near {arguments['project_path']}",
                )
            ]
        col_name = collection_name_for(context_dir)

    store = get_vector_store()

    if not await store.collection_exists(col_name):
        return [
            types.TextContent(
                type="text",
                text=f"Collection '{col_name}' not found. Run index_project_context first.",
            )
        ]

    # --- Provenance mismatch check ---
    warning_prefix = ""
    stored_meta = await store.get_collection_metadata(col_name)
    current_provider = get_embedding_provider()
    stored_embed_provider = stored_meta.get("embed_provider", "")
    stored_embed_model = stored_meta.get("embed_model", "")

    if stored_embed_provider and stored_embed_model:
        if stored_embed_provider != current_provider.provider_name or stored_embed_model != current_provider.model_name:
            warning_prefix = _MISMATCH_WARNING.format(
                old_provider=stored_embed_provider,
                old_model=stored_embed_model,
                new_provider=current_provider.provider_name,
                new_model=current_provider.model_name,
            )

    try:
        provider = get_embedding_provider()
        query_embedding = await provider.embed_chunk(query)
        result = await store.query(
            collection_name=col_name,
            query_embedding=query_embedding,
            n_results=n_results,
        )
    except (VectorStoreError, EmbeddingError) as exc:
        return [types.TextContent(type="text", text=f"Search failed: {exc}")]

    if not result.documents:
        return [types.TextContent(type="text", text=f"{warning_prefix}No results found.")]

    output_parts = [f"**[{meta.get('file', '?')}]**\n{doc}" for doc, meta in zip(result.documents, result.metadatas)]
    body = "\n\n---\n\n".join(output_parts)
    return [types.TextContent(type="text", text=f"{warning_prefix}{body}")]
