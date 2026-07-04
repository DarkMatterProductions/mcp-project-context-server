"""Google Gemini API embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`GOOGLE_API_KEY`
    API key for the Google Generative AI service.  **Required.**

`GOOGLE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `gemini-embedding-2`.
"""

import asyncio
import os

from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider
from mcp_project_context_server.exceptions import EmbeddingError

_DEFAULT_MODEL: str = "gemini-embedding-2"
# gemini-embedding-2: 2048 token context; conservative character limit
_MAX_CHARS: int = 24_000


class GoogleEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Google Generative AI (Gemini) API.

    The `google.generativeai` package is imported lazily inside `embed_chunk()` so
    that the provider can be imported without requiring the package to be installed.
    Because the `genai.embed_content` function is synchronous, it is wrapped with
    `asyncio.to_thread` to avoid blocking the event loop.

    Raises:
        EnvironmentError: At construction time if `GOOGLE_API_KEY` is not set.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("GOOGLE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "google"

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
        """Embed *text* using the configured Google Generative AI embedding model.

        Args:
            text: Text to embed.  Should be at most `max_chars` long.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            EmbeddingError: If the Google API returns an error or is unreachable.
        """
        try:
            import google.generativeai as genai  # lazy import

            genai.configure(api_key=self._api_key)
            result = await asyncio.to_thread(genai.embed_content, model=self._model, content=text)
            return list(result["embedding"])
        except Exception as exc:
            raise EmbeddingError(f"Google embedding failed (model={self._model}): {exc}") from exc
