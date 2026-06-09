"""VectorStoreProvider Protocol — the provider abstraction boundary for vector storage.

All vector store providers must implement this Protocol so that the rest of the
codebase can depend on the abstraction rather than any concrete backend.

Usage
-----
::

    from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider
    from mcp_project_context_server.integrations.vectorstore.registry import get_vector_store

    store = get_vector_store()
    collection = await store.get_or_create_collection("my-project")
"""
import logging
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Results returned from a vector similarity query."""

    ids: list[str]
    documents: list[str]
    metadatas: list[dict]
    distances: list[float] = field(default_factory=list)


@runtime_checkable
class VectorStoreProvider(Protocol):
    """Protocol that all vector store provider implementations must satisfy.

    Implementations must be safe to import without triggering network connections
    or filesystem I/O — those should be deferred to first method call.
    """

    @property
    def provider_name(self) -> str:
        """Short identifier, e.g. ``"chroma-local"``, ``"pgvector"``."""
        ...

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Create a collection, replacing it if it already exists.

        Implements the drop-and-recreate strategy (ADR-00006): any existing
        collection with *name* is deleted before the new one is created.

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        ...

    async def delete_collection(self, name: str) -> None:
        """Delete a collection.  Silently succeeds if it does not exist.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        ...

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Insert or update documents in a collection.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        """
        ...

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a nearest-neighbour search against a collection.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist or the query fails.
        """
        ...

    async def count(self, collection_name: str) -> int:
        """Return the number of documents stored in *collection_name*.

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        ...

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if *collection_name* exists in this store.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        ...

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return the metadata dict stored on a collection.

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection
            does not exist.
        """
        ...


class VectorStoreError(Exception):
    """Raised when a vector store operation fails."""
