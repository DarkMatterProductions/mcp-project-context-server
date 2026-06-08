"""Google Vertex AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

``GOOGLE_VERTEX_PROJECT``
    Google Cloud project ID.  **Required.**

``GOOGLE_VERTEX_LOCATION``
    Google Cloud region, e.g. ``us-central1``.  **Required.**

``GOOGLE_VERTEX_EMBED_MODEL``
    Name of the embedding model to use.  Defaults to ``text-embedding-004``.
"""

import asyncio
import os

from mcp_project_context_server.integrations.embeddings.base import EmbeddingError

_DEFAULT_MODEL: str = "text-embedding-004"
# Conservative character limit matching the model's context window
_MAX_CHARS: int = 24_000


class GoogleVertexEmbeddingProvider:
    """Embedding provider backed by the Google Vertex AI SDK.

    The ``vertexai`` package is imported lazily inside ``embed()`` so that the
    provider can be imported without requiring the package to be installed.
    Because the Vertex AI SDK is synchronous, calls are wrapped with
    ``asyncio.to_thread`` to avoid blocking the event loop.

    Raises:
        EnvironmentError: At construction time if ``GOOGLE_VERTEX_PROJECT`` or
            ``GOOGLE_VERTEX_LOCATION`` are not set.
    """

    def __init__(self) -> None:
        """Initialise the provider, reading configuration from environment variables."""
        project = os.getenv("GOOGLE_VERTEX_PROJECT")
        if not project:
            raise EnvironmentError("GOOGLE_VERTEX_PROJECT environment variable is not set.")
        location = os.getenv("GOOGLE_VERTEX_LOCATION")
        if not location:
            raise EnvironmentError("GOOGLE_VERTEX_LOCATION environment variable is not set.")
        self._project: str = project
        self._location: str = location
        self._model: str = os.getenv("GOOGLE_VERTEX_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "google_vertex"

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
        """Embed *text* using the configured Vertex AI embedding model.

        Args:
            text: Text to embed.  Should be at most ``max_chars`` long.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            EmbeddingError: If the Vertex AI SDK returns an error or is unreachable.
        """
        try:
            import vertexai  # lazy import
            from vertexai.language_models import TextEmbeddingModel  # lazy import

            vertexai.init(project=self._project, location=self._location)
            model = TextEmbeddingModel.from_pretrained(self._model)
            embeddings = await asyncio.to_thread(model.get_embeddings, [text])
            return list(embeddings[0].values)
        except Exception as exc:
            raise EmbeddingError(
                f"Google Vertex AI embedding failed (project={self._project}, model={self._model}): {exc}"
            ) from exc
