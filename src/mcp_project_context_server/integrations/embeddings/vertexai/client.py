"""Google Vertex AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`VERTEXAI_PROJECT`
    Google Cloud project ID.  **Required.**

`VERTEXAI_LOCATION`
    Google Cloud region, e.g. `us-central1`.  **Required.**

`VERTEXAI_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `text-embedding-004`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "text-embedding-004"
# Conservative character limit matching the model's context window
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class GoogleVertexEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Google Vertex AI SDK.

    The `vertexai` package is imported lazily inside `_get_embedding_model()`
    so that the provider can be constructed without requiring the package to
    be installed unless it is actually used. The `TextEmbeddingModel` is
    resolved on first use and cached for subsequent calls.

    The SDK is configured with `api_transport="rest"` to force plain HTTP
    instead of gRPC. gRPC's C-core polling engine (used by both its
    synchronous and `grpc.aio` async clients) can deadlock when it shares a
    process with asyncio's `ProactorEventLoop` — the loop this server
    requires on Windows for stdio subprocess support. REST has no such
    conflict, so the embedding call is made with the synchronous
    `get_embeddings()` wrapped in `asyncio.to_thread`, same as every other
    HTTP-based provider in this package.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `VERTEXAI_PROJECT` or `VERTEXAI_LOCATION` are not set.
        """
        project = os.getenv("VERTEXAI_PROJECT")
        if not project:
            raise EnvironmentError("VERTEXAI_PROJECT environment variable is not set.")
        location = os.getenv("VERTEXAI_LOCATION")
        if not location:
            raise EnvironmentError("VERTEXAI_LOCATION environment variable is not set.")
        self._project: str = project
        self._location: str = location
        self._model: str = os.getenv("VERTEXAI_EMBED_MODEL", _DEFAULT_MODEL)
        self._embedding_model = None

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "vertexai"

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

    def _get_embedding_model(self):
        """Resolve and cache the `TextEmbeddingModel`, initializing the SDK on first use.

        Configures the SDK to use REST rather than gRPC — see the class
        docstring for why gRPC is unsafe in this server's event loop.
        """
        if self._embedding_model is None:
            import vertexai  # lazy import
            from vertexai.language_models import TextEmbeddingModel  # lazy import

            vertexai.init(project=self._project, location=self._location, api_transport="rest")
            self._embedding_model = TextEmbeddingModel.from_pretrained(self._model)
        return self._embedding_model

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Vertex AI embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Vertex AI SDK returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            model = self._get_embedding_model()
            embeddings = await asyncio.wait_for(
                asyncio.to_thread(model.get_embeddings, [text]),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(embeddings[0].values)
        except Exception as exc:
            raise EmbeddingError(
                f"Google Vertex AI embedding failed (project={self._project}, model={self._model}): {exc}"
            ) from exc
