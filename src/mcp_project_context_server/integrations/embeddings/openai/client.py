"""OpenAI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

``OPENAI_API_KEY``
    API key for the OpenAI service.  **Required.**

``OPENAI_EMBED_MODEL``
    Name of the embedding model to use.  Defaults to ``text-embedding-3-small``.
"""

import os

from mcp_project_context_server.integrations.embeddings.base import EmbeddingError

_DEFAULT_MODEL: str = "text-embedding-3-small"
# text-embedding-3-small: 8191 token context; conservative character limit
_MAX_CHARS: int = 24_000


class OpenAIEmbeddingProvider:
    """Embedding provider backed by the OpenAI Embeddings API.

    The ``openai`` package is imported lazily inside ``embed()`` so that the
    provider can be imported without requiring the package to be installed.

    Raises:
        EnvironmentError: At construction time if ``OPENAI_API_KEY`` is not set.
    """

    def __init__(self) -> None:
        """Initialise the provider, reading configuration from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("OPENAI_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "openai"

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
        """Embed *text* using the configured OpenAI embedding model.

        Args:
            text: Text to embed.  Should be at most ``max_chars`` long.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            EmbeddingError: If the OpenAI API returns an error or is unreachable.
        """
        try:
            from openai import AsyncOpenAI  # lazy import

            client = AsyncOpenAI(api_key=self._api_key)
            response = await client.embeddings.create(model=self._model, input=text)
            return list(response.data[0].embedding)
        except Exception as exc:
            raise EmbeddingError(f"OpenAI embedding failed (model={self._model}): {exc}") from exc
