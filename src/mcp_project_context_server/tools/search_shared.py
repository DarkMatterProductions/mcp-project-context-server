"""Shared semantic-search implementation used by the `search_*_index`/`search_session_files` tools.

Before executing a search, the tool reads the provenance metadata stored on
the collection at index time and compares it against the current provider
configuration.  If the embedding provider or model has changed, a warning is
prepended to the results so the user knows the index may need rebuilding.
"""
import logging
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
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreError
from mcp_project_context_server.integrations.vectorstore.registry import get_vector_store

logger = logging.getLogger(__name__)

_MISMATCH_WARNING = (
    "⚠️  **Provider mismatch detected** — the index was built with "
    "`{old_provider}/{old_model}` but the current provider is "
    "`{new_provider}/{new_model}`.  Search results may be inaccurate.  "
    "Please re-run `index_project_context` to rebuild the index.\n\n---\n\n"
)

# Floor applied to the over-fetch multiplier so a small `n_results` still
# pulls in enough candidates for the client-side prefix filter to find hits.
_OVER_FETCH_FLOOR = 25
_OVER_FETCH_MULTIPLIER = 5


def _empty_result(text: str) -> types.CallToolResult:
    """Build a `CallToolResult` for an early-return/error path with no hits."""
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        structured_content={"results": []},
    )


async def run_search(
    project_path: str, query: str, n_results: int, file_prefix: str | None = None
) -> types.CallToolResult:
    """Run a semantic search over the indexed `.context/` collection.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param query: (str) The natural-language search query.
    :param n_results: (int) The number of results to return to the caller.
    :param file_prefix: (str) When set, only hits whose ``metadata["file"]`` starts
        with this prefix are returned (used to scope search to ``decisions/`` or
        ``sessions/``). The store is over-fetched so the filter still has enough
        candidates to select from.
    :return: (CallToolResult) The unstructured text (matching context snippets,
        optionally prefixed with a provider/model mismatch warning, or an
        error/"not found" message) alongside a ``structured_content`` object of
        the shape ``{"results": [{"file", "chunk", "content", "distance"}, ...]}``.
    """
    try:
        validate_repo_access(project_path)
    except RepositoryError as exc:
        return _empty_result(str(exc))

    repo_provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(project_path, repo_provider.provider_name)

    if is_remote:
        col_name = collection_name_for_repo_id(resolved_path)
    else:
        context_dir = find_context_dir(resolved_path)
        if not context_dir:
            return _empty_result(f"No .context/ directory found near {project_path}")
        col_name = collection_name_for(context_dir)

    store = get_vector_store()

    if not await store.collection_exists(col_name):
        return _empty_result(f"Collection '{col_name}' not found. Run index_project_context first.")

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

    query_n_results = n_results
    if file_prefix is not None:
        query_n_results = max(n_results * _OVER_FETCH_MULTIPLIER, _OVER_FETCH_FLOOR)

    try:
        provider = get_embedding_provider()
        query_embedding = await provider.embed_chunk(query)
        result = await store.query(
            collection_name=col_name,
            query_embedding=query_embedding,
            n_results=query_n_results,
        )
    except (VectorStoreError, EmbeddingError) as exc:
        return _empty_result(f"Search failed: {exc}")

    documents = result.documents
    metadatas = result.metadatas
    distances = result.distances if len(result.distances) == len(documents) else [None] * len(documents)

    if file_prefix is not None:
        filtered = [
            (doc, meta, dist)
            for doc, meta, dist in zip(documents, metadatas, distances)
            if meta.get("file", "").startswith(file_prefix)
        ]
        filtered = filtered[:n_results]
        documents = [doc for doc, _, _ in filtered]
        metadatas = [meta for _, meta, _ in filtered]
        distances = [dist for _, _, dist in filtered]

    if not documents:
        return _empty_result(f"{warning_prefix}No results found.")

    items = [
        {"file": meta.get("file", "?"), "chunk": meta.get("chunk"), "content": doc, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
    output_parts = [f"**[{item['file']}]**\n{item['content']}" for item in items]
    body = "\n\n---\n\n".join(output_parts)

    structured_content: dict = {"results": items}
    if warning_prefix:
        structured_content["warning"] = warning_prefix.strip()

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"{warning_prefix}{body}")],
        structured_content=structured_content,
    )
