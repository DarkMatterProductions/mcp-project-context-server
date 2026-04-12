"""Embedding generation for the indexing pipeline."""

from project_context_server.integrations.ollama.client import get_embedding


def embed_chunk(text: str) -> list[float]:
    """Generate an embedding vector for a single text chunk."""
    return get_embedding(text)