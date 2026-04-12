"""Ollama client configuration and raw embedding API calls (sync + async)."""

import os
import ollama

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")


def get_client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def get_async_client() -> ollama.AsyncClient:
    return ollama.AsyncClient(host=OLLAMA_BASE_URL)


def get_embedding(text: str) -> list[float]:
    """Call the Ollama embed endpoint and return the embedding vector."""
    response = get_client().embed(model=EMBED_MODEL, input=text)
    return list(response.embeddings[0])


async def get_embedding_async(text: str, client: ollama.AsyncClient) -> list[float]:
    """Async: Call the Ollama embed endpoint and return the embedding vector."""
    response = await client.embed(model=EMBED_MODEL, input=text)
    return list(response.embeddings[0])
