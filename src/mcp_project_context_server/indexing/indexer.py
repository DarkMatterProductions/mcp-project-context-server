"""Shared indexing pipeline — provider-agnostic core.

Accepts any ``VectorStoreProvider`` instance.  Vector-store-specific indexers
in ``integrations/vectorstore/{provider}/indexer.py`` are responsible for
instantiating their own provider and passing it here.

No vector-store or embedding provider is imported directly.  All external
dependencies are injected via the ``store`` parameter and the embedding
registry.
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

from mcp_project_context_server.helpers.context import (
    collection_name_for,
    collection_name_for_repo_id,
    find_context_dir,
    read_context_files,
    resolve_project_path,
)
from mcp_project_context_server.helpers.context_files import hash_content
from mcp_project_context_server.helpers.sections import chunk_section, split_sections
from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider

logger = logging.getLogger(__name__)

_EMBED_CONCURRENCY: int = int(os.getenv("EMBED_CONCURRENCY", "4"))
_MAX_CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1500"))


async def run_index_pipeline(project_path: str | Path, store: VectorStoreProvider) -> str:
    """Chunk, embed concurrently, and batch-store all .context/ markdown files.

    Stamps the collection with provenance metadata (embed provider/model,
    vector store provider, repo provider, server version, indexed_at timestamp)
    so that search can detect and warn on provider/model mismatches.

    :param project_path: (str) Path to the project root or any file within it.
    :param store: (VectorStoreProvider) Fully initialized vector store provider to write into.
    :return: (str) A human-readable summary string describing what was indexed.
    """
    repo_provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(str(project_path), repo_provider.provider_name)

    if is_remote:
        try:
            files = await repo_provider.fetch_context_files(resolved_path)
        except RepositoryError as exc:
            return f"Error accessing repository {resolved_path}: {exc}"
        if not files:
            return f"No .context/ directory found in {resolved_path}"
        col_name = collection_name_for_repo_id(resolved_path)
    else:
        context_dir = find_context_dir(project_path)
        if not context_dir:
            return f"No .context/ directory found at or above {project_path}"
        col_name = collection_name_for(context_dir)
        files = read_context_files(context_dir)

    # Deferred until after the context-existence check above so that a
    # missing .context/ directory is reported even when no embedding
    # provider is configured (EMBED_PROVIDER unset).
    embed_provider = get_embedding_provider()
    max_chars = min(_MAX_CHUNK_SIZE, embed_provider.max_chars)
    embed_chunk = embed_provider.embed_chunk

    collection_metadata = {
        "embed_provider": embed_provider.provider_name,
        "embed_model": embed_provider.model_name,
        "vector_store_provider": store.provider_name,
        "repo_provider": repo_provider.provider_name,
        "server_version": __version__,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }

    await store.create_collection(col_name, metadata=collection_metadata)

    all_chunks: list[tuple[str, str, str, int, str, str]] = []
    for filename, file_content in files.items():
        chunk_idx = 0
        for section in split_sections(file_content):
            section_sha512 = hash_content(section.content)
            for piece in chunk_section(section, max_chars):
                if piece.strip():
                    all_chunks.append((f"{filename}::{chunk_idx}", piece, filename, chunk_idx, section.name, section_sha512))
                    chunk_idx += 1

    if not all_chunks:
        return f"Indexed 0 chunks from {len(files)} files into collection '{col_name}'"

    semaphore = asyncio.Semaphore(_EMBED_CONCURRENCY)

    async def _embed(doc_id: str, chunk: str, filename: str, chunk_idx: int, section: str, section_sha512: str):
        async with semaphore:
            try:
                embedding = await embed_chunk(chunk)
                return (doc_id, chunk, embedding, filename, chunk_idx, section, section_sha512)
            except Exception as e:
                logger.warning("Failed to embed %s: %s", doc_id, e)
                return e

    results = await asyncio.gather(*[_embed(*c) for c in all_chunks])

    valid = [r for r in results if not isinstance(r, Exception)]
    if valid:
        await store.upsert(
            collection_name=col_name,
            ids=[r[0] for r in valid],
            embeddings=[r[2] for r in valid],
            documents=[r[1] for r in valid],
            metadatas=[{"file": r[3], "chunk": r[4], "section": r[5], "section_sha512": r[6]} for r in valid],
        )

    failed_count = len(all_chunks) - len(valid)
    if failed_count == len(all_chunks):
        first_error = next(r for r in results if isinstance(r, Exception))
        return (
            f"Error: failed to embed all {len(all_chunks)} chunks from {len(files)} files "
            f"— 0 chunks indexed. First error: {first_error}"
        )
    if failed_count:
        return (
            f"Indexed {len(valid)} chunks from {len(files)} files into collection '{col_name}' "
            f"({failed_count} chunks failed to embed — see server logs)"
        )

    return f"Indexed {len(valid)} chunks from {len(files)} files into collection '{col_name}'"
