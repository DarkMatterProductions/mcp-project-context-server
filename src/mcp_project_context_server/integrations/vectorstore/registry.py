"""Vector store provider registry — factory driven by ``VECTOR_STORE_PROVIDER`` env var.

Design rules
------------
* ``chroma-local`` is the **default** when ``VECTOR_STORE_PROVIDER`` is not set.
  This preserves backward compatibility for local developer setups.
* Unknown values raise ``EnvironmentError`` immediately at startup (fail-fast).
* The provider singleton is cached after the first call.

Supported ``VECTOR_STORE_PROVIDER`` values
------------------------------------------
``chroma-local`` *(default)*
    Local ChromaDB PersistentClient.  Requires ``CHROMA_DIR`` (optional,
    defaults to ``~/.mcp-data/chroma``).

``chroma-http``
    Remote ChromaDB HTTP server.  Requires ``CHROMA_HOST``, ``CHROMA_PORT``
    (optional, defaults to ``localhost:8000``).  Optional: ``CHROMA_API_KEY``.

``pgvector``
    PostgreSQL with the pgvector extension.  Requires
    ``PGVECTOR_CONNECTION_STRING``.
"""

import os
from typing import Optional

from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"chroma-local", "chroma-http", "pgvector"})
_DEFAULT_PROVIDER: str = "chroma-local"

_provider_instance: Optional[VectorStoreProvider] = None


def get_vector_store() -> VectorStoreProvider:
    """Return the configured vector store provider singleton.

    Raises:
        EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value,
            or if the selected provider is missing a required env var.
        ImportError: If the required package for the selected provider is not installed.
    """
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    _provider_instance = _build_provider(provider_name)
    return _provider_instance


def _build_provider(provider_name: str) -> VectorStoreProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "chroma-local":
        from mcp_project_context_server.integrations.vectorstore.chroma_local.client import (
            ChromaLocalVectorStoreProvider,
        )
        return ChromaLocalVectorStoreProvider()

    if provider_name == "chroma-http":
        from mcp_project_context_server.integrations.vectorstore.chroma_http.client import (
            ChromaHttpVectorStoreProvider,
        )
        return ChromaHttpVectorStoreProvider()

    if provider_name == "pgvector":
        from mcp_project_context_server.integrations.vectorstore.pgvector.client import (
            PgVectorStoreProvider,
        )
        return PgVectorStoreProvider()

    raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover


def reset_provider_for_testing() -> None:
    """Reset the cached provider singleton.  **For use in tests only.**"""
    global _provider_instance
    _provider_instance = None
