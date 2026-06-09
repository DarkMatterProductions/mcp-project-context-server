"""Cohere embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

``COHERE_API_KEY``
    API key for the Cohere service.  **Required.**

``COHERE_EMBED_MODEL``
    Name of the embedding model to use.  Defaults to ``embed-english-v3.0``.
"""

import os

from mcp_project_context_server.integrations.embeddings.base import EmbeddingError

_DEFAULT_MODEL: str = "embed-english-v3.0"
# embed-english-v3.0: 512 token context; conservative character limit
_MAX_CHARS: int = 20_000


class CohereEmbeddingProvider:
    """Embedding provider backed by the Cohere Embed API.

    The ``cohere`` package is imported lazily inside ``embed()`` so that the
    provider can be imported without requiring the package to be installed.

    Raises:
        EnvironmentError: At construction time if ``COHERE_API_KEY`` is not set.
    """

    def __init__(self) -> None:
        """Initialise the provider, reading configuration from environment variables."""
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

    async def embed(self, text: str) -> list[float]:
        """Embed *text* using the configured Cohere embedding model.

        Args:
            text: Text to embed.  Should be at most ``max_chars`` long.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            EmbeddingError: If the Cohere API returns an error or is unreachable.
        """
        try:
            import cohere  # lazy import

            client = cohere.AsyncClientV2(api_key=self._api_key)
            response = await client.embed(
                texts=[text],
                model=self._model,
                input_type="search_document",
                embedding_types=["float"],
            )
            return list(response.embeddings.float_[0])
        except Exception as exc:
            raise EmbeddingError(f"Cohere embedding failed (model={self._model}): {exc}") from exc
