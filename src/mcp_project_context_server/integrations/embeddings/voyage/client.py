"""Voyage AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`VOYAGE_API_KEY`
    API key for the Voyage AI service.  **Required.**

`VOYAGE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `voyage-code-3`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "voyage-code-3"
# voyage-code-3 context ≈ 32k tokens; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class VoyageEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Voyage AI API.

    The `voyageai` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `VOYAGE_API_KEY` is not set.
        """
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            raise EnvironmentError("VOYAGE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("VOYAGE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "voyage"

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
        """Embed *text* using the configured Voyage AI model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Voyage AI API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import voyageai  # lazy import

            client = voyageai.AsyncClient(api_key=self._api_key)
            result = await asyncio.wait_for(
                client.embed([text], model=self._model, input_type="document"),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(result.embeddings[0])
        except Exception as exc:
            raise EmbeddingError(f"Voyage AI embedding failed (model={self._model}): {exc}") from exc
