"""Ollama client configuration and raw embedding API call."""

import os
import ollama

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")


def get_client() -> ollama.Client:
    return ollama.Client(host=OLLAMA_BASE_URL)


def get_embedding(text: str) -> list[float]:
    """Call the Ollama embeddings endpoint and return the embedding vector."""
    response = get_client().embeddings(model=EMBED_MODEL, prompt=text)
    return response["embedding"]