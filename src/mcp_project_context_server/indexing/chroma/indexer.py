"""Indexes .context/ files into ChromaDB for semantic search."""

import asyncio
import importlib.metadata
import os
import sys
from pathlib import Path

from mcp_project_context_server.helpers.context import (
    collection_name_for,
    find_context_dir,
    read_context_files,
)
from mcp_project_context_server.indexing.chunker import chunk_markdown
from mcp_project_context_server.indexing.ollama.embedder import embed_chunk_async
from mcp_project_context_server.integrations.chroma.client import chroma_client
from mcp_project_context_server.integrations.ollama.client import get_async_client

_EMBED_CONCURRENCY: int = int(os.getenv("EMBED_CONCURRENCY", "4"))
_CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1500"))

try:
    _SERVER_VERSION: str = importlib.metadata.version("mcp-project-context-server")
except importlib.metadata.PackageNotFoundError:
    _SERVER_VERSION = "unknown"


async def index_project_context(project_path: str | Path) -> str:
    """Chunk, embed concurrently, and batch-store all .context/ markdown files."""
    context_dir = find_context_dir(project_path)
    if not context_dir:
        return f"No .context/ directory found at or above {project_path}"

    col_name = collection_name_for(context_dir)

    # Drop and recreate for a clean re-index
    try:
        chroma_client.delete_collection(col_name)
    except Exception:
        pass
    collection = chroma_client.create_collection(
        col_name,
        metadata={"server_version": _SERVER_VERSION},
    )

    files = read_context_files(context_dir)

    # Build flat list of (doc_id, chunk_text, source_posix, chunk_index)
    all_chunks: list[tuple[str, str, str, int]] = []
    for source_posix, file_content in files.items():
        for i, chunk in enumerate(chunk_markdown(file_content, _CHUNK_SIZE)):
            all_chunks.append((f"{source_posix}::chunk::{i}", chunk, source_posix, i))

    if not all_chunks:
        return f"Indexed 0 chunks from {len(files)} files into collection '{col_name}'"

    # Embed all chunks concurrently, bounded by semaphore
    async_client = get_async_client()
    semaphore = asyncio.Semaphore(_EMBED_CONCURRENCY)

    async def _embed(doc_id: str, chunk: str, source_posix: str, chunk_idx: int):
        async with semaphore:
            try:
                embedding = await embed_chunk_async(chunk, async_client)
                return (doc_id, chunk, embedding, source_posix, chunk_idx)
            except Exception as e:
                print(f"Warning: failed to embed {doc_id}: {e}", file=sys.stderr)
                return None

    results = await asyncio.gather(*[_embed(*c) for c in all_chunks])

    # Filter failures, then batch-add everything to ChromaDB in one call
    valid = [r for r in results if r is not None]
    if valid:
        collection.add(
            ids=[r[0] for r in valid],
            embeddings=[r[2] for r in valid],
            documents=[r[1] for r in valid],
            metadatas=[{"source": r[3], "chunk": r[4]} for r in valid],
        )

    return f"Indexed {len(valid)} chunks from {len(files)} files into collection '{col_name}'"
