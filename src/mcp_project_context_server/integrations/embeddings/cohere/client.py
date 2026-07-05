"""Cohere embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`COHERE_API_KEY`
    API key for the Cohere service.  **Required.**

`COHERE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `embed-english-v3.0`.
"""

import asyncio
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

_DEFAULT_MODEL: str = "embed-english-v3.0"
# embed-english-v3.0: 512 token context; conservative character limit
_MAX_CHARS: int = 20_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class CohereEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Cohere Embed API.

    The `cohere` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `COHERE_API_KEY` is not set.
        """
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise EnvironmentError("COHERE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("COHERE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "cohere"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Cohere embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Cohere API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import cohere  # lazy import

            client = cohere.AsyncClientV2(api_key=self._api_key)
            response = await asyncio.wait_for(
                client.embed(
                    texts=[text],
                    model=self._model,
                    input_type="search_document",
                    embedding_types=["float"],
                ),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.embeddings.float_[0])
        except Exception as exc:
            raise EmbeddingError(f"Cohere embedding failed (model={self._model}): {exc}") from exc
