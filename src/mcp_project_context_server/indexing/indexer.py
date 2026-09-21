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
from dataclasses import dataclass
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


@dataclass(frozen=True)
class _Chunk:
    """A single chunk of file content, addressed by a content-derived ID.

    :param id: (str) ``f"{filename}::{section}::{segment}-{section_sha512}"``.
    :param text: (str) The chunk's raw text.
    :param filename: (str) The source file this chunk was extracted from.
    :param segment: (int) Sub-chunk index within its section, reset to 0 per section.
    :param section: (str) The section heading this chunk belongs to.
    :param section_sha512: (str) SHA-512 of the *whole section's* content (shared by all of
        that section's sub-chunks).
    """

    id: str
    text: str
    filename: str
    segment: int
    section: str
    section_sha512: str


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

    all_chunks: list[_Chunk] = []
    seen_ids: set[str] = set()
    for filename, file_content in files.items():
        for section in split_sections(file_content):
            section_sha512 = hash_content(section.content)
            for segment, piece in enumerate(chunk_section(section, max_chars)):
                if not piece.strip():
                    continue
                chunk_id = f"{filename}::{section.name}::{segment}-{section_sha512}"
                if chunk_id in seen_ids:
                    logger.warning("Duplicate chunk ID %s — keeping first occurrence", chunk_id)
                    continue
                seen_ids.add(chunk_id)
                all_chunks.append(_Chunk(chunk_id, piece, filename, segment, section.name, section_sha512))

    expected_ids = {c.id for c in all_chunks}
    existing_ids = set(await store.list_ids(col_name))
    to_embed = [c for c in all_chunks if c.id not in existing_ids]
    to_delete = sorted(existing_ids - expected_ids)
    unchanged_count = len(all_chunks) - len(to_embed)

    semaphore = asyncio.Semaphore(_EMBED_CONCURRENCY)

    async def _embed(chunk: _Chunk):
        async with semaphore:
            try:
                embedding = await embed_chunk(chunk.text)
                return (chunk, embedding)
            except Exception as e:
                logger.warning("Failed to embed %s: %s", chunk.id, e)
                return e

    # Nothing destructive has happened yet: the store is untouched up to this
    # point, so any embedding failure below can still abort without data loss.
    results = await asyncio.gather(*[_embed(c) for c in to_embed])

    # asyncio.gather preserves input order, so this pairing recovers which
    # file/section each failure belongs to without changing _embed's return shape.
    failed = [(chunk, result) for chunk, result in zip(to_embed, results) if isinstance(result, Exception)]

    if failed:
        # All-or-nothing: abort without calling ensure_collection, upsert, or delete_by_ids.
        # The previously indexed collection, if any, is left completely intact.
        preview = "; ".join(f"{chunk.filename}::{chunk.section} ({exc})" for chunk, exc in failed[:10])
        more = f"; +{len(failed) - 10} more" if len(failed) > 10 else ""
        return (
            f"Error: failed to embed {len(failed)}/{len(to_embed)} chunks from {len(files)} files "
            f"— aborting without modifying collection '{col_name}' (previous index, if any, is unchanged). "
            f"Failed chunks: {preview}{more}"
        )

    # Every chunk embedded successfully. Metadata is refreshed on every run,
    # even a no-op reindex, since `indexed_at` means "last time indexing ran".
    await store.ensure_collection(col_name, metadata=collection_metadata)
    if results:
        await store.upsert(
            collection_name=col_name,
            ids=[chunk.id for chunk, _ in results],
            embeddings=[embedding for _, embedding in results],
            documents=[chunk.text for chunk, _ in results],
            metadatas=[
                {"file": chunk.filename, "chunk": chunk.segment, "section": chunk.section, "section_sha512": chunk.section_sha512}
                for chunk, _ in results
            ],
        )
    if to_delete:
        await store.delete_by_ids(col_name, to_delete)

    return (
        f"Indexed {len(all_chunks)} chunks from {len(files)} files into collection '{col_name}' "
        f"({len(to_embed)} embedded, {unchanged_count} unchanged, {len(to_delete)} removed)"
    )
