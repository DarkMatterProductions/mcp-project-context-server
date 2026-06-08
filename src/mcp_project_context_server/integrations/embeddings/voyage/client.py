"""Voyage AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

``VOYAGE_API_KEY``
    API key for the Voyage AI service.  **Required.**

``VOYAGE_EMBED_MODEL``
    Name of the embedding model to use.  Defaults to ``voyage-code-3``.
"""

import os

from mcp_project_context_server.integrations.embeddings.base import EmbeddingError


_DEFAULT_MODEL: str = "voyage-code-3"
# voyage-code-3 context ≈ 32k tokens; conservative character limit
_MAX_CHARS: int = 24_000


class VoyageEmbeddingProvider:
    """Embedding provider backed by the Voyage AI API.

    The ``voyageai`` package is imported lazily inside ``embed()`` so that the
    provider can be imported without requiring the package to be installed.

    Raises:
        EnvironmentError: At construction time if ``VOYAGE_API_KEY`` is not set.
    """

    def __init__(self) -> None:
        """Initialise the provider, reading configuration from environment variables."""
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

    async def embed(self, text: str) -> list[float]:
        """Embed *text* using the configured Voyage AI model.

        Args:
            text: Text to embed.  Should be at most ``max_chars`` long.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            EmbeddingError: If the Voyage AI API returns an error or is unreachable.
        """
        try:
            import voyageai  # lazy import

            client = voyageai.AsyncClient(api_key=self._api_key)
            result = await client.embed([text], model=self._model, input_type="document")
            return list(result.embeddings[0])
        except Exception as exc:
            raise EmbeddingError(
                f"Voyage AI embedding failed (model={self._model}): {exc}"
            ) from exc
