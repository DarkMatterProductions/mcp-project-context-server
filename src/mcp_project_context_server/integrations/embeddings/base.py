"""EmbeddingProvider Protocol — the provider abstraction boundary for embeddings.

All embedding providers must implement this Protocol so that the rest of the
codebase can depend on the abstraction rather than any concrete provider.

Usage
-----
Import the protocol for type annotations::

    from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

Obtain a concrete instance from the registry::

    from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
    provider = get_embedding_provider()
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol that all embedding provider implementations must satisfy.

    Implementors should be importable without triggering any network calls,
    file I/O, or expensive initialisation — those should be deferred to the
    first call to ``embed()``.
    """

    @property
    def provider_name(self) -> str:
        """Short identifier for the provider, e.g. ``"ollama"``, ``"voyage"``."""
        ...

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use, e.g. ``"nomic-embed-text"``."""
        ...

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters for this model.

        Used by the chunking layer to stay within the provider's context window.
        This is an advisory value — providers may silently truncate longer inputs.
        """
        ...

    async def embed(self, text: str) -> list[float]:
        """Embed a single text string and return the embedding vector.

        Args:
            text: The text to embed.  May be up to ``max_chars`` in length.

        Returns:
            A list of floats representing the embedding vector.

        Raises:
            EmbeddingError: If the provider returns an error or is unreachable.
        """
        ...
