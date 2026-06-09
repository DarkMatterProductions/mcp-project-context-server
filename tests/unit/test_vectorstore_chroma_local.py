"""Tests for ChromaLocalVectorStoreProvider (integrations/vectorstore/chroma_local/client.py).

All chromadb calls are mocked — no real filesystem or ChromaDB required.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)
from mcp_project_context_server.integrations.vectorstore.chroma_local.client import (
    ChromaLocalVectorStoreProvider,
)


@pytest.fixture()
def provider() -> ChromaLocalVectorStoreProvider:
    p = ChromaLocalVectorStoreProvider()
    p.reset_for_testing()
    return p


@pytest.fixture()
def mock_client(provider: ChromaLocalVectorStoreProvider) -> MagicMock:
    """Inject a mock chromadb client directly — avoids patching the lazy import."""
    client = MagicMock()
    provider._client = client
    return client


# ---------------------------------------------------------------------------
# CHROMA_DIR resolution
# ---------------------------------------------------------------------------


class TestChromaDirResolution:
    def test_tilde_prefixed_chroma_dir_is_expanded_to_home(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CHROMA_DIR", "~/.mcp-data/Projects/example/chroma")
        provider = ChromaLocalVectorStoreProvider()
        assert provider._dir == Path.home() / ".mcp-data" / "Projects" / "example" / "chroma"
        assert "~" not in provider._dir.parts

    def test_absolute_chroma_dir_is_unchanged(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("CHROMA_DIR", str(tmp_path))
        provider = ChromaLocalVectorStoreProvider()
        assert provider._dir == tmp_path


# ---------------------------------------------------------------------------
# provider_name
# ---------------------------------------------------------------------------


class TestProviderName:
    def test_provider_name(self, provider: ChromaLocalVectorStoreProvider) -> None:
        assert provider.provider_name == "chroma-local"


# ---------------------------------------------------------------------------
# create_collection
# ---------------------------------------------------------------------------


class TestCreateCollection:
    @pytest.mark.asyncio
    async def test_create_collection_drops_and_recreates(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        await provider.create_collection("my-col", metadata={"k": "v"})
        mock_client.delete_collection.assert_called_once_with("my-col")
        mock_client.create_collection.assert_called_once_with(name="my-col", metadata={"k": "v"})

    @pytest.mark.asyncio
    async def test_create_collection_silently_handles_delete_failure(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.delete_collection.side_effect = Exception("no such collection")
        # Should not raise
        await provider.create_collection("new-col")
        mock_client.create_collection.assert_called_once_with(name="new-col", metadata={})


# ---------------------------------------------------------------------------
# delete_collection
# ---------------------------------------------------------------------------


class TestDeleteCollection:
    @pytest.mark.asyncio
    async def test_delete_collection_calls_client(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        await provider.delete_collection("col")
        mock_client.delete_collection.assert_called_once_with("col")

    @pytest.mark.asyncio
    async def test_delete_collection_silently_handles_missing(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.delete_collection.side_effect = Exception("not found")
        await provider.delete_collection("missing")  # must not raise


# ---------------------------------------------------------------------------
# upsert
# ---------------------------------------------------------------------------


class TestUpsert:
    @pytest.mark.asyncio
    async def test_upsert_calls_col_add(self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock) -> None:
        mock_col = MagicMock()
        mock_client.get_collection.return_value = mock_col

        await provider.upsert(
            collection_name="col",
            ids=["1", "2"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["doc1", "doc2"],
            metadatas=[{"f": "a"}, {"f": "b"}],
        )

        mock_client.get_collection.assert_called_once_with("col")
        mock_col.add.assert_called_once_with(
            ids=["1", "2"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["doc1", "doc2"],
            metadatas=[{"f": "a"}, {"f": "b"}],
        )

    @pytest.mark.asyncio
    async def test_upsert_raises_vector_store_error_when_collection_not_found(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.side_effect = Exception("not found")
        with pytest.raises(VectorStoreError, match="not found"):
            await provider.upsert(
                collection_name="missing",
                ids=["1"],
                embeddings=[[0.1]],
                documents=["doc"],
                metadatas=[{}],
            )


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------


class TestQuery:
    @pytest.mark.asyncio
    async def test_query_returns_query_result_with_correct_fields(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_col = MagicMock()
        mock_col.count.return_value = 2
        mock_client.get_collection.return_value = mock_col
        mock_col.query.return_value = {
            "ids": [["id1", "id2"]],
            "documents": [["Doc 1", "Doc 2"]],
            "metadatas": [[{"file": "a.md"}, {"file": "b.md"}]],
            "distances": [[0.9, 0.8]],
        }

        result = await provider.query("col", [0.1, 0.2], n_results=2)

        assert result.ids == ["id1", "id2"]
        assert result.documents == ["Doc 1", "Doc 2"]
        assert result.metadatas == [{"file": "a.md"}, {"file": "b.md"}]
        assert result.distances == [0.9, 0.8]

    @pytest.mark.asyncio
    async def test_query_returns_empty_result_when_count_is_zero(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_col = MagicMock()
        mock_col.count.return_value = 0
        mock_client.get_collection.return_value = mock_col

        result = await provider.query("col", [0.1, 0.2])

        assert result == QueryResult(ids=[], documents=[], metadatas=[], distances=[])
        mock_col.query.assert_not_called()

    @pytest.mark.asyncio
    async def test_query_raises_vector_store_error_when_collection_not_found(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.side_effect = Exception("missing")
        with pytest.raises(VectorStoreError):
            await provider.query("missing", [0.1])


# ---------------------------------------------------------------------------
# count
# ---------------------------------------------------------------------------


class TestCount:
    @pytest.mark.asyncio
    async def test_count_returns_integer(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_col = MagicMock()
        mock_col.count.return_value = 42
        mock_client.get_collection.return_value = mock_col

        result = await provider.count("col")
        assert result == 42

    @pytest.mark.asyncio
    async def test_count_returns_zero_when_collection_absent(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.side_effect = Exception("gone")
        result = await provider.count("missing")
        assert result == 0


# ---------------------------------------------------------------------------
# collection_exists
# ---------------------------------------------------------------------------


class TestCollectionExists:
    @pytest.mark.asyncio
    async def test_returns_true_when_collection_found(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.return_value = MagicMock()
        assert await provider.collection_exists("col") is True

    @pytest.mark.asyncio
    async def test_returns_false_when_collection_not_found(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.side_effect = Exception("nope")
        assert await provider.collection_exists("missing") is False


# ---------------------------------------------------------------------------
# get_collection_metadata
# ---------------------------------------------------------------------------


class TestGetCollectionMetadata:
    @pytest.mark.asyncio
    async def test_returns_metadata_dict(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_col = MagicMock()
        mock_col.metadata = {"version": "1"}
        mock_client.get_collection.return_value = mock_col

        result = await provider.get_collection_metadata("col")
        assert result == {"version": "1"}

    @pytest.mark.asyncio
    async def test_returns_empty_dict_on_error(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.side_effect = Exception("error")
        result = await provider.get_collection_metadata("missing")
        assert result == {}


# ---------------------------------------------------------------------------
# reset_for_testing
# ---------------------------------------------------------------------------


class TestResetForTesting:
    def test_reset_for_testing_clears_cached_client(
        self, provider: ChromaLocalVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        # client was injected by mock_client fixture
        assert provider._client is not None
        provider.reset_for_testing()
        assert provider._client is None
