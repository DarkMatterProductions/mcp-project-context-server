"""Provider-agnostic embedding entry point for the indexing pipeline.

This module is the **only** place in the indexing pipeline that calls into an
embedding provider.  It obtains the configured provider from the registry and
delegates all embedding work to it.

No provider-specific imports live here.  Adding or swapping providers requires
only changes to ``integrations/embeddings/`` — the indexing pipeline is
unaffected.
"""

from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider


async def embed_chunk(text: str) -> list[float]:
    """Embed a single text chunk using the configured embedding provider.

    Args:
        text: The text chunk to embed.

    Returns:
        Embedding vector as a list of floats.

    Raises:
        EnvironmentError: If ``EMBED_PROVIDER`` is not configured.
        EmbeddingError: If the provider call fails.
    """
    provider = get_embedding_provider()
    return await provider.embed(text)


def get_max_chars() -> int:
    """Return the maximum chunk size (in characters) for the active provider.

    Used by the chunking layer in ``indexer.py`` to stay within the provider's
    context window.

    Raises:
        EnvironmentError: If ``EMBED_PROVIDER`` is not configured.
    """
    provider = get_embedding_provider()
    return provider.max_chars
