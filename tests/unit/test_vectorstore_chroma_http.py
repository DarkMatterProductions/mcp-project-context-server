"""Tests for ChromaHttpVectorStoreProvider (integrations/vectorstore/chroma_http/client.py).

All chromadb calls are mocked — no real network or ChromaDB required.
"""

from unittest.mock import MagicMock

import pytest

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)
from mcp_project_context_server.integrations.vectorstore.chroma_http.client import (
    ChromaHttpVectorStoreProvider,
)

_CHROMADB_PATH = "mcp_project_context_server.integrations.vectorstore.chroma_http.client.chromadb"


@pytest.fixture()
def provider() -> ChromaHttpVectorStoreProvider:
    p = ChromaHttpVectorStoreProvider()
    p.reset_for_testing()
    return p


@pytest.fixture()
def mock_client(provider: ChromaHttpVectorStoreProvider) -> MagicMock:
    """Inject a mock chromadb HTTP client directly."""
    client = MagicMock()
    provider._client = client
    return client


# ---------------------------------------------------------------------------
# provider_name
# ---------------------------------------------------------------------------


class TestProviderName:
    def test_provider_name(self, provider: ChromaHttpVectorStoreProvider) -> None:
        assert provider.provider_name == "chroma-http"


# ---------------------------------------------------------------------------
# Environment variable configuration
# ---------------------------------------------------------------------------


class TestEnvVarConfig:
    def test_default_host_and_port_when_env_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_HOST", raising=False)
        monkeypatch.delenv("CHROMA_PORT", raising=False)
        monkeypatch.delenv("CHROMA_API_KEY", raising=False)
        p = ChromaHttpVectorStoreProvider()
        assert p._host == "localhost"
        assert p._port == 8000
        assert p._api_key is None

    def test_custom_host_port_and_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CHROMA_HOST", "remote-host")
        monkeypatch.setenv("CHROMA_PORT", "9000")
        monkeypatch.setenv("CHROMA_API_KEY", "secret")
        p = ChromaHttpVectorStoreProvider()
        assert p._host == "remote-host"
        assert p._port == 9000
        assert p._api_key == "secret"


# ---------------------------------------------------------------------------
# Settings auth config (tested by inspecting _get_client() calls)
# ---------------------------------------------------------------------------


class TestSettingsAuthConfig:
    def test_no_auth_config_when_api_key_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import sys

        monkeypatch.delenv("CHROMA_API_KEY", raising=False)
        p = ChromaHttpVectorStoreProvider()
        p.reset_for_testing()

        captured: list[dict] = []
        mock_settings_cls = MagicMock(side_effect=lambda **kw: (captured.append(kw), MagicMock())[1])
        mock_chromadb = MagicMock()
        mock_chromadb.HttpClient.return_value = MagicMock()

        # Inject a fake chromadb.config.Settings via sys.modules so that
        # `from chromadb.config import Settings` picks up our mock.
        fake_config_mod = MagicMock()
        fake_config_mod.Settings = mock_settings_cls
        monkeypatch.setitem(sys.modules, "chromadb", mock_chromadb)
        monkeypatch.setitem(sys.modules, "chromadb.config", fake_config_mod)
        mock_chromadb.config = fake_config_mod

        p._get_client()

        assert all(
            "chroma_client_auth_provider" not in c for c in captured
        ), f"Unexpected auth provider in settings calls: {captured}"

    def test_auth_config_included_when_api_key_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import sys

        monkeypatch.setenv("CHROMA_API_KEY", "my-secret")
        p = ChromaHttpVectorStoreProvider()
        p.reset_for_testing()

        captured: list[dict] = []
        mock_settings_cls = MagicMock(side_effect=lambda **kw: (captured.append(kw), MagicMock())[1])
        mock_chromadb = MagicMock()
        mock_chromadb.HttpClient.return_value = MagicMock()

        fake_config_mod = MagicMock()
        fake_config_mod.Settings = mock_settings_cls
        monkeypatch.setitem(sys.modules, "chromadb", mock_chromadb)
        monkeypatch.setitem(sys.modules, "chromadb.config", fake_config_mod)
        mock_chromadb.config = fake_config_mod

        p._get_client()

        auth_calls = [c for c in captured if "chroma_client_auth_provider" in c]
        assert len(auth_calls) == 1
        assert auth_calls[0]["chroma_client_auth_credentials"] == "my-secret"


# ---------------------------------------------------------------------------
# create_collection
# ---------------------------------------------------------------------------


class TestCreateCollection:
    @pytest.mark.asyncio
    async def test_create_collection_drops_and_recreates(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        await provider.create_collection("my-col", metadata={"k": "v"})
        mock_client.delete_collection.assert_called_once_with("my-col")
        mock_client.create_collection.assert_called_once_with(name="my-col", metadata={"k": "v"})

    @pytest.mark.asyncio
    async def test_create_collection_silently_handles_delete_failure(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.delete_collection.side_effect = Exception("no such collection")
        await provider.create_collection("new-col")
        mock_client.create_collection.assert_called_once_with(name="new-col", metadata={})


# ---------------------------------------------------------------------------
# delete_collection
# ---------------------------------------------------------------------------


class TestDeleteCollection:
    @pytest.mark.asyncio
    async def test_delete_collection_calls_client(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        await provider.delete_collection("col")
        mock_client.delete_collection.assert_called_once_with("col")

    @pytest.mark.asyncio
    async def test_delete_collection_silently_handles_missing(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.delete_collection.side_effect = Exception("not found")
        await provider.delete_collection("missing")  # must not raise


# ---------------------------------------------------------------------------
# upsert
# ---------------------------------------------------------------------------


class TestUpsert:
    @pytest.mark.asyncio
    async def test_upsert_calls_col_add(self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock) -> None:
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
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
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
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
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
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_col = MagicMock()
        mock_col.count.return_value = 0
        mock_client.get_collection.return_value = mock_col

        result = await provider.query("col", [0.1, 0.2])

        assert result == QueryResult(ids=[], documents=[], metadatas=[], distances=[])
        mock_col.query.assert_not_called()

    @pytest.mark.asyncio
    async def test_query_raises_vector_store_error_when_collection_not_found(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.side_effect = Exception("missing")
        with pytest.raises(VectorStoreError):
            await provider.query("missing", [0.1])


# ---------------------------------------------------------------------------
# count
# ---------------------------------------------------------------------------


class TestCount:
    @pytest.mark.asyncio
    async def test_count_returns_integer(self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock) -> None:
        mock_col = MagicMock()
        mock_col.count.return_value = 7
        mock_client.get_collection.return_value = mock_col

        result = await provider.count("col")
        assert result == 7

    @pytest.mark.asyncio
    async def test_count_returns_zero_when_collection_absent(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
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
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.return_value = MagicMock()
        assert await provider.collection_exists("col") is True

    @pytest.mark.asyncio
    async def test_returns_false_when_collection_not_found(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.side_effect = Exception("nope")
        assert await provider.collection_exists("missing") is False


# ---------------------------------------------------------------------------
# get_collection_metadata
# ---------------------------------------------------------------------------


class TestGetCollectionMetadata:
    @pytest.mark.asyncio
    async def test_returns_metadata_dict(self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock) -> None:
        mock_col = MagicMock()
        mock_col.metadata = {"version": "2"}
        mock_client.get_collection.return_value = mock_col

        result = await provider.get_collection_metadata("col")
        assert result == {"version": "2"}

    @pytest.mark.asyncio
    async def test_returns_empty_dict_on_error(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        mock_client.get_collection.side_effect = Exception("error")
        result = await provider.get_collection_metadata("missing")
        assert result == {}


# ---------------------------------------------------------------------------
# reset_for_testing
# ---------------------------------------------------------------------------


class TestResetForTesting:
    def test_reset_for_testing_clears_cached_client(
        self, provider: ChromaHttpVectorStoreProvider, mock_client: MagicMock
    ) -> None:
        assert provider._client is not None
        provider.reset_for_testing()
        assert provider._client is None
