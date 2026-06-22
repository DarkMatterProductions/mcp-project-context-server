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
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.chroma_http.client import ChromaHttpVectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.chroma_local.client import ChromaLocalVectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.pgvector.client import PgVectorStoreProvider

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"chroma-local", "chroma-http", "pgvector"})
_DEFAULT_PROVIDER: str = "chroma-local"

IndexFn = Callable[[str | Path], Coroutine[Any, Any, str]]


def get_vector_store() -> VectorStoreProvider:
    """Return the configured vector store provider singleton.

    Raises:
        EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value,
            or if the selected provider is missing a required env var.
        ImportError: If the required package for the selected provider is not installed.
    """
    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    return _build_provider(provider_name)


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


def get_indexer() -> IndexFn:
    """Return the ``index_project_context`` callable for the configured provider.

    Each vector store provider owns its indexer in
    ``integrations/vectorstore/{provider}/indexer.py``.  This function resolves
    the correct one based on ``VECTOR_STORE_PROVIDER``, mirroring the dispatch
    logic of :func:`get_vector_store`.

    Raises:
        EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value.
    """
    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    if provider_name == "chroma-local":
        store = ChromaLocalVectorStoreProvider()
    elif provider_name == "chroma-http":
        store = ChromaHttpVectorStoreProvider()
    elif provider_name == "pgvector":
        store = PgVectorStoreProvider()
    else:
        raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover

    async def index_project_context(project_path: str | Path) -> str:
        """Run the indexing pipeline against a local ChromaDB PersistentClient.

        Args:
            project_path: Path to the project root or any file within it.

        Returns:
            A human-readable summary string describing what was indexed.
        """

        return await run_index_pipeline(project_path, store)

    return index_project_context
