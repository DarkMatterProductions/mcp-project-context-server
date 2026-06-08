"""Tests for integrations/vectorstore/base.py — QueryResult, VectorStoreProvider, VectorStoreError."""

from typing import Any

import pytest

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
    VectorStoreProvider,
)


# ---------------------------------------------------------------------------
# QueryResult dataclass
# ---------------------------------------------------------------------------


class TestQueryResult:
    def test_default_distances_is_empty_list(self) -> None:
        qr = QueryResult(ids=["a"], documents=["doc"], metadatas=[{"k": "v"}])
        assert qr.distances == []

    def test_all_fields_set_correctly(self) -> None:
        qr = QueryResult(
            ids=["id1", "id2"],
            documents=["doc1", "doc2"],
            metadatas=[{"file": "a.md"}, {"file": "b.md"}],
            distances=[0.9, 0.8],
        )
        assert qr.ids == ["id1", "id2"]
        assert qr.documents == ["doc1", "doc2"]
        assert qr.metadatas == [{"file": "a.md"}, {"file": "b.md"}]
        assert qr.distances == [0.9, 0.8]

    def test_distances_default_factory_creates_independent_lists(self) -> None:
        """Each instance gets its own default distances list (no shared state)."""
        qr1 = QueryResult(ids=[], documents=[], metadatas=[])
        qr2 = QueryResult(ids=[], documents=[], metadatas=[])
        qr1.distances.append(1.0)
        assert qr2.distances == []


# ---------------------------------------------------------------------------
# VectorStoreProvider Protocol — isinstance checks
# ---------------------------------------------------------------------------


class _CompleteProvider:
    """A class that implements every method in the VectorStoreProvider Protocol."""

    @property
    def provider_name(self) -> str:
        return "complete"

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        pass

    async def delete_collection(self, name: str) -> None:
        pass

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        pass

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        return QueryResult(ids=[], documents=[], metadatas=[])

    async def count(self, collection_name: str) -> int:
        return 0

    async def collection_exists(self, collection_name: str) -> bool:
        return False

    async def get_collection_metadata(self, collection_name: str) -> dict:
        return {}


class _IncompleteProvider:
    """A class that is missing several Protocol methods."""

    @property
    def provider_name(self) -> str:
        return "incomplete"

    # Missing: create_collection, delete_collection, upsert, query, count,
    #          collection_exists, get_collection_metadata


class TestVectorStoreProviderProtocol:
    def test_complete_class_satisfies_protocol(self) -> None:
        provider = _CompleteProvider()
        assert isinstance(provider, VectorStoreProvider)

    def test_incomplete_class_does_not_satisfy_protocol(self) -> None:
        provider = _IncompleteProvider()
        assert not isinstance(provider, VectorStoreProvider)


# ---------------------------------------------------------------------------
# VectorStoreError
# ---------------------------------------------------------------------------


class TestVectorStoreError:
    def test_is_exception_subclass(self) -> None:
        assert issubclass(VectorStoreError, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(VectorStoreError, match="boom"):
            raise VectorStoreError("boom")

    def test_can_be_caught_as_generic_exception(self) -> None:
        with pytest.raises(Exception):
            raise VectorStoreError("generic catch")
