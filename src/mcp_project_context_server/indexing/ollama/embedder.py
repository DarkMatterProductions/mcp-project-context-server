"""Embedding generation for the indexing pipeline (sync + async).

The functions here are the single access point for embedding within the indexing
pipeline.  They deliberately accept only standard Python types so that no
provider-specific imports (ollama, openai, etc.) bleed into this layer.
The caller is responsible for passing a client object whose interface matches
what the underlying provider expects — provider coupling lives in
integrations/*/client.py, not here.
"""

from typing import Any

from mcp_project_context_server.integrations.ollama.client import (
    get_embedding,
    get_embedding_async,
)


def embed_chunk(text: str) -> list[float]:
    """Generate an embedding vector for a single text chunk."""
    return get_embedding(text)


async def embed_chunk_async(text: str, client: Any) -> list[float]:
    """Async: Generate an embedding vector for a single text chunk.

    Args:
        text:   The text to embed.
        client: An async client object whose interface is resolved by the
                underlying provider implementation.  Typed as ``Any`` so that
                this module remains free of provider-specific imports.
    """
    return await get_embedding_async(text, client)
