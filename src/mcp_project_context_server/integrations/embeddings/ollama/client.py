"""Ollama embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`OLLAMA_HOST`
    Base URL for the Ollama server.  Defaults to `http://localhost:11434`.

`OLLAMA_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `nomic-embed-text`.

`EMBED_CONCURRENCY`
    Maximum number of concurrent embedding requests.  Defaults to `4`.
    (Respected by the caller — not enforced here.)
"""

import asyncio
import os

from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

from mcp_project_context_server.exceptions import EmbeddingError

_DEFAULT_HOST: str = "http://localhost:11434"
_DEFAULT_MODEL: str = "nomic-embed-text"
# Conservative character limit for nomic-embed-text (8192 token context ≈ 32 000 chars)
_MAX_CHARS: int = 32_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by a locally running Ollama server.

    This class is intentionally stateless with respect to the Ollama client —
    a fresh `AsyncClient` is obtained per call so that there are no
    long-lived connection objects to manage.
    """

    def __init__(self) -> None:
        self._host: str = os.getenv("OLLAMA_HOST", _DEFAULT_HOST)
        self._model: str = os.getenv("OLLAMA_EMBED_MODEL", os.getenv("EMBED_MODEL", _DEFAULT_MODEL))

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def max_chars(self) -> int:
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Ollama model.

        Args:
            text: Text to embed.  Should be at most `max_chars` long.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            EmbeddingError: If the Ollama server returns an error, is
                unreachable, or does not respond within the timeout.
        """
        try:
            import ollama
            client = ollama.Client(host=self._host)
            response = await asyncio.wait_for(
                asyncio.to_thread(client.embed, model=self._model, input=text),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.embeddings[0])
        except Exception as exc:
            raise EmbeddingError(f"Ollama embedding failed (host={self._host}, model={self._model}): {exc}") from exc
