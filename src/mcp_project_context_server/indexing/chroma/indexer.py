"""Indexes .context/ files into the configured vector store for semantic search.

Provider-agnostic: embedding via ``indexing/embedder.py``, vector storage via
``integrations/vectorstore/registry.py``.  Neither the embedding provider nor
the vector store implementation is imported directly here.
"""

import asyncio
import os
import sys
from pathlib import Path

from mcp_project_context_server.helpers.context import (
    collection_name_for,
    find_context_dir,
    read_context_files,
)
from mcp_project_context_server.indexing.embedder import embed_chunk, get_max_chars
from mcp_project_context_server.integrations.vectorstore.registry import get_vector_store

_EMBED_CONCURRENCY: int = int(os.getenv("EMBED_CONCURRENCY", "4"))


async def index_project_context(project_path: str | Path) -> str:
    """Chunk, embed concurrently, and batch-store all .context/ markdown files.

    Chunk size is driven by the active embedding provider's ``max_chars``
    so that chunks stay within the model's context window.

    Args:
        project_path: Path to the project root or any file within it.

    Returns:
        A human-readable summary string describing what was indexed.
    """
    context_dir = find_context_dir(project_path)
    if not context_dir:
        return f"No .context/ directory found at or above {project_path}"

    col_name = collection_name_for(context_dir)
    chunk_size = get_max_chars()
    store = get_vector_store()

    # Drop and recreate for a clean re-index (ADR-00006)
    await store.create_collection(col_name)

    files = read_context_files(context_dir)

    # Build flat list of (doc_id, chunk_text, filename, chunk_index)
    all_chunks: list[tuple[str, str, str, int]] = []
    for filename, file_content in files.items():
        for i, chunk in enumerate(
            file_content[j : j + chunk_size] for j in range(0, len(file_content), chunk_size)
        ):
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
                print(f"Warning: failed to embed {doc_id}: {e}", file=sys.stderr)
                return None

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
