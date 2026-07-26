"""OpenAI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`OPENAI_API_KEY`
    API key for the OpenAI service.  **Required.**

`OPENAI_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `text-embedding-3-small`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "text-embedding-3-small"
# text-embedding-3-small: 8191 token context; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the OpenAI Embeddings API.

    The `openai` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `OPENAI_API_KEY` is not set.
        """
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

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured OpenAI embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the OpenAI API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            from openai import AsyncOpenAI  # lazy import

            client = AsyncOpenAI(api_key=self._api_key)
            response = await asyncio.wait_for(
                client.embeddings.create(model=self._model, input=text),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.data[0].embedding)
        except Exception as exc:
            raise EmbeddingError(f"OpenAI embedding failed (model={self._model}): {exc}") from exc
