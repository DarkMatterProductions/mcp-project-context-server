"""Embedding generation for the indexing pipeline (sync + async)."""

import ollama

from mcp_project_context_server.integrations.ollama.client import (
    get_embedding,
    get_embedding_async,
)


def embed_chunk(text: str) -> list[float]:
    """Generate an embedding vector for a single text chunk."""
    return get_embedding(text)


async def embed_chunk_async(text: str, client: ollama.AsyncClient) -> list[float]:
    """Async: Generate an embedding vector for a single text chunk."""
    return await get_embedding_async(text, client)
