"""Embedding provider registry — factory driven by the ``EMBED_PROVIDER`` env var.

Design rules
------------
* **Fail fast at startup** if ``EMBED_PROVIDER`` is not set or the value is
  unrecognised.  There is no silent fallback to Ollama or any other provider.
  Explicit configuration is required.
* Importing this module does **not** initialise any provider.  Call
  ``get_embedding_provider()`` to obtain a provider instance.
* The returned instance is cached after the first call so that repeated
  calls within a process return the same object.

Usage
-----
::

    from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider

    provider = get_embedding_provider()
    vector = await provider.embed("some text")

Supported ``EMBED_PROVIDER`` values
------------------------------------
``ollama``
    Local Ollama server.  Requires ``OLLAMA_HOST`` (default: http://localhost:11434)
    and optionally ``OLLAMA_EMBED_MODEL`` (default: nomic-embed-text).

``voyage``
    Voyage AI cloud API.  Requires ``VOYAGE_API_KEY``.
    Optional: ``VOYAGE_EMBED_MODEL`` (default: voyage-code-3).

``openai``
    OpenAI cloud API.  Requires ``OPENAI_API_KEY``.
    Optional: ``OPENAI_EMBED_MODEL`` (default: text-embedding-3-small).

``cohere``
    Cohere cloud API.  Requires ``COHERE_API_KEY``.
    Optional: ``COHERE_EMBED_MODEL`` (default: embed-english-v3.0).

``google``
    Google Gemini API (google-generativeai).  Requires ``GOOGLE_API_KEY``.
    Optional: ``GOOGLE_EMBED_MODEL`` (default: text-embedding-004).

``google-vertex``
    Google Vertex AI.  Requires ``GOOGLE_VERTEX_PROJECT`` and
    ``GOOGLE_VERTEX_LOCATION``.
    Optional: ``GOOGLE_VERTEX_EMBED_MODEL`` (default: text-embedding-004).
"""

import os
from typing import Optional

from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"ollama", "voyage", "openai", "cohere", "google", "google-vertex"})

_provider_instance: Optional[EmbeddingProvider] = None


def get_embedding_provider() -> EmbeddingProvider:
    """Return the configured embedding provider singleton.

    Raises:
        EnvironmentError: If ``EMBED_PROVIDER`` is not set or is not one of
            the supported provider names.
        ImportError: If the required package for the selected provider is not
            installed.
    """
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_name = os.getenv("EMBED_PROVIDER", "").strip().lower()

    if not provider_name:
        raise EnvironmentError(
            "EMBED_PROVIDER environment variable is not set.  "
            f"Set it to one of: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported EMBED_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    _provider_instance = _build_provider(provider_name)
    return _provider_instance


def _build_provider(provider_name: str) -> EmbeddingProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "ollama":
        from mcp_project_context_server.integrations.embeddings.ollama.client import (
            OllamaEmbeddingProvider,
        )

        return OllamaEmbeddingProvider()

    if provider_name == "voyage":
        from mcp_project_context_server.integrations.embeddings.voyage.client import (
            VoyageEmbeddingProvider,
        )

        return VoyageEmbeddingProvider()

    if provider_name == "openai":
        from mcp_project_context_server.integrations.embeddings.openai.client import (
            OpenAIEmbeddingProvider,
        )

        return OpenAIEmbeddingProvider()

    if provider_name == "cohere":
        from mcp_project_context_server.integrations.embeddings.cohere.client import (
            CohereEmbeddingProvider,
        )

        return CohereEmbeddingProvider()

    if provider_name == "google":
        from mcp_project_context_server.integrations.embeddings.google.client import (
            GoogleEmbeddingProvider,
        )

        return GoogleEmbeddingProvider()

    if provider_name == "google-vertex":
        from mcp_project_context_server.integrations.embeddings.google_vertex.client import (
            GoogleVertexEmbeddingProvider,
        )

        return GoogleVertexEmbeddingProvider()

    # Should never reach here — guarded by the caller.
    raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover


def reset_provider_for_testing() -> None:
    """Reset the cached provider singleton.

    **For use in tests only.**  Call this in test teardown to prevent provider
    state from leaking between test cases that set different ``EMBED_PROVIDER``
    values.
    """
    global _provider_instance
    _provider_instance = None
