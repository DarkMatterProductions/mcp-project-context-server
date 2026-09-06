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

``gcp-vector-search``
    Google Cloud Vertex AI Vector Search against a pre-provisioned Index and
    IndexEndpoint (ADR-00023; this provider does not create or deploy GCP
    infrastructure).  Requires ``GCP_VECTOR_SEARCH_PROJECT``,
    ``GCP_VECTOR_SEARCH_LOCATION``, ``GCP_VECTOR_SEARCH_INDEX_ID``,
    ``GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID``, and
    ``GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID``.  Optional:
    ``GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION``.

Incompatible combinations
-------------------------
``EMBED_PROVIDER=vertexai`` cannot be combined with ``chroma-local`` or
``chroma-http``: the two SDKs deadlock when loaded into the same process on
Windows.  Use ``VECTOR_STORE_PROVIDER=pgvector`` with Vertex AI instead.
"""
import logging
import os
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

from mcp_project_context_server.indexing.indexer import run_index_pipeline
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.chroma_http.client import ChromaHttpVectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.chroma_local.client import ChromaLocalVectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import GcpVectorSearchProvider
from mcp_project_context_server.integrations.vectorstore.pgvector.client import PgVectorStoreProvider

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"chroma-local", "chroma-http", "pgvector", "gcp-vector-search"})
_DEFAULT_PROVIDER: str = "chroma-local"

# EMBED_PROVIDER values that cannot share a process with the given
# VECTOR_STORE_PROVIDER.  The vertexai SDK and the chromadb client (both of
# which pull in native/C-extension dependencies) deadlock when imported into
# the same Windows process -- this is an in-process native-library conflict,
# not a credentials or network issue, so it cannot be worked around by
# retrying or adding timeouts.
INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE: dict[str, frozenset[str]] = {
    "chroma-local": frozenset({"vertexai"}),
    "chroma-http": frozenset({"vertexai"}),
}

IndexFn = Callable[[str | Path], Coroutine[Any, Any, str]]


def _assert_compatible_providers(vector_store_provider_name: str) -> None:
    """Raise if the configured EMBED_PROVIDER cannot be used with *vector_store_provider_name*."""
    embed_provider_name = os.getenv("EMBED_PROVIDER", "").strip().lower()
    incompatible = INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE.get(vector_store_provider_name, frozenset())
    if embed_provider_name in incompatible:
        raise EnvironmentError(
            f"EMBED_PROVIDER='{embed_provider_name}' cannot be used with "
            f"VECTOR_STORE_PROVIDER='{vector_store_provider_name}': these two SDKs "
            "deadlock when loaded into the same process on Windows.  Use "
            "VECTOR_STORE_PROVIDER=pgvector with EMBED_PROVIDER=vertexai instead."
        )


def get_vector_store() -> VectorStoreProvider:
    """Return the configured vector store provider singleton.

    :return: (VectorStoreProvider) The vector store provider instance selected by
        ``VECTOR_STORE_PROVIDER`` (defaults to ``"chroma-local"``).
    :raises EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value,
        if the selected provider is missing a required env var, or if the
        configured ``EMBED_PROVIDER`` is incompatible with it.
    :raises ImportError: If the required package for the selected provider is not installed.
    """
    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    _assert_compatible_providers(provider_name)

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

    if provider_name == "gcp-vector-search":
        from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import (
            GcpVectorSearchProvider,
        )

        return GcpVectorSearchProvider()

    raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover


def get_indexer() -> IndexFn:
    """Return the ``index_project_context`` callable for the configured provider.

    Each vector store provider owns its indexer in
    ``integrations/vectorstore/{provider}/indexer.py``.  This function resolves
    the correct one based on ``VECTOR_STORE_PROVIDER``, mirroring the dispatch
    logic of :func:`get_vector_store`.

    :return: (Callable) An async callable that indexes a project path and
        returns a human-readable summary string.
    :raises EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value,
        or if the configured ``EMBED_PROVIDER`` is incompatible with it.
    """
    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    _assert_compatible_providers(provider_name)

    if provider_name == "chroma-local":
        store = ChromaLocalVectorStoreProvider()
    elif provider_name == "chroma-http":
        store = ChromaHttpVectorStoreProvider()
    elif provider_name == "pgvector":
        store = PgVectorStoreProvider()
    elif provider_name == "gcp-vector-search":
        store = GcpVectorSearchProvider()
    else:
        raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover

    async def index_project_context(project_path: str | Path) -> str:
        """Run the indexing pipeline against a local ChromaDB PersistentClient.

        :param project_path: (str) Path to the project root or any file within it.
        :return: (str) A human-readable summary string describing what was indexed.
        """

        return await run_index_pipeline(project_path, store)

    return index_project_context
