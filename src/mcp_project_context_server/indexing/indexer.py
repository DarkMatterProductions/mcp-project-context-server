"""Shared indexing pipeline — provider-agnostic core.

Accepts any ``VectorStoreProvider`` instance.  Vector-store-specific indexers
in ``integrations/vectorstore/{provider}/indexer.py`` are responsible for
instantiating their own provider and passing it here.

No vector-store or embedding provider is imported directly.  All external
dependencies are injected via the ``store`` parameter and the embedding
registry.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from mcp_project_context_server.exceptions import EmbeddingError

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

from mcp_project_context_server.helpers.context import (
    collection_name_for,
    find_context_dir,
    read_context_files,
)
from mcp_project_context_server.indexing.embedder import embed_chunk, get_max_chars
from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from mcp_project_context_server.integrations.repository.registry import get_repository_provider
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider

_EMBED_CONCURRENCY: int = int(os.getenv("EMBED_CONCURRENCY", "4"))


async def run_index_pipeline(project_path: str | Path, store: VectorStoreProvider) -> str:
    """Chunk, embed concurrently, and batch-store all .context/ markdown files.

    Stamps the collection with provenance metadata (embed provider/model,
    vector store provider, repo provider, server version, indexed_at timestamp)
    so that search can detect and warn on provider/model mismatches.

    Args:
        project_path: Path to the project root or any file within it.
        store: Fully initialised vector store provider to write into.

    Returns:
        A human-readable summary string describing what was indexed.
    """
    context_dir = find_context_dir(project_path)
    if not context_dir:
        return f"No .context/ directory found at or above {project_path}"

    col_name = collection_name_for(context_dir)
    chunk_size = get_max_chars()
    embed_provider = get_embedding_provider()
    repo_provider = get_repository_provider()

    collection_metadata = {
        "embed_provider": embed_provider.provider_name,
        "embed_model": embed_provider.model_name,
        "vector_store_provider": store.provider_name,
        "repo_provider": repo_provider.provider_name,
        "server_version": __version__,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }

    await store.create_collection(col_name, metadata=collection_metadata)

    files = read_context_files(context_dir)

    all_chunks: list[tuple[str, str, str, int]] = []
    for filename, file_content in files.items():
        for i, chunk in enumerate(file_content[j : j + chunk_size] for j in range(0, len(file_content), chunk_size)):
            if chunk.strip():
                all_chunks.append((f"{filename}::{i}", chunk, filename, i))

    if not all_chunks:
        return f"Indexed 0 chunks from {len(files)} files into collection '{col_name}'"

    semaphore = asyncio.Semaphore(_EMBED_CONCURRENCY)

    async def _embed(doc_id: str, chunk: str, filename: str, chunk_idx: int):
        async with semaphore:
            try:
                embedding = await embed_chunk(chunk)
                return (doc_id, chunk, embedding, filename, chunk_idx)
            except Exception as e:
                raise EmbeddingError(f"Warning: failed to embed {doc_id}: {e}")

    results = await asyncio.gather(*[_embed(*c) for c in all_chunks])

    valid = [r for r in results if r is not None]
    if valid:
        await store.upsert(
            collection_name=col_name,
            ids=[r[0] for r in valid],
            embeddings=[r[2] for r in valid],
            documents=[r[1] for r in valid],
            metadatas=[{"file": r[3], "chunk": r[4]} for r in valid],
        )

    return f"Indexed {len(valid)} chunks from {len(files)} files into collection '{col_name}'"
