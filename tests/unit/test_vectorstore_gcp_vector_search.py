"""Tests for GcpVectorSearchProvider (integrations/vectorstore/gcp_vector_search/client.py).

google-cloud-aiplatform and google-cloud-firestore are mocked completely -- no real
GCP project required. Provider construction and most methods never import the SDKs
directly (mock handles are pre-injected instead, bypassing the lazy `_get_index`/
`_get_endpoint`/`_get_firestore` singletons). `query()` additionally imports
`Namespace` from `google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint`
on every call; that import path is stubbed via `sys.modules`, mirroring the
`asyncpg`-mocking approach used for the pgvector provider tests.
"""

import sys
import types
from unittest.mock import MagicMock

import pytest

_REQUIRED_ENV = {
    "GCP_VECTOR_SEARCH_PROJECT": "proj",
    "GCP_VECTOR_SEARCH_LOCATION": "us-central1",
    "GCP_VECTOR_SEARCH_INDEX_ID": "idx-1",
    "GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID": "ep-1",
    "GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID": "deployed-1",
}

_NAMESPACE_MODULE = "google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint"


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in _REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_namespace(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Stub the ``Namespace`` class imported lazily inside ``query()``."""
    fake_mod = types.ModuleType(_NAMESPACE_MODULE)
    namespace_cls = MagicMock()
    fake_mod.Namespace = namespace_cls
    monkeypatch.setitem(sys.modules, _NAMESPACE_MODULE, fake_mod)
    return namespace_cls


@pytest.fixture()
def provider(monkeypatch: pytest.MonkeyPatch):
    _set_required_env(monkeypatch)
    from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import (
        GcpVectorSearchProvider,
    )

    p = GcpVectorSearchProvider()
    p.reset_for_testing()
    return p


@pytest.fixture()
def wired_provider(provider):
    """Provider with pre-injected mock SDK handles -- bypasses lazy init entirely."""
    provider._index = MagicMock()
    provider._endpoint = MagicMock()
    provider._firestore = MagicMock()
    return provider


# ---------------------------------------------------------------------------
# __init__ guard
# ---------------------------------------------------------------------------


class TestInit:
    @pytest.mark.parametrize("missing_var", sorted(_REQUIRED_ENV))
    def test_raises_environment_error_when_required_var_missing(
        self, monkeypatch: pytest.MonkeyPatch, missing_var: str
    ) -> None:
        _set_required_env(monkeypatch)
        monkeypatch.delenv(missing_var, raising=False)
        from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import (
            GcpVectorSearchProvider,
        )

        with pytest.raises(EnvironmentError, match=missing_var):
            GcpVectorSearchProvider()

    def test_defaults_firestore_collection_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_required_env(monkeypatch)
        monkeypatch.delenv("GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION", raising=False)
        from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import (
            GcpVectorSearchProvider,
        )

        p = GcpVectorSearchProvider()
        assert p._firestore_collection == "vector_store_documents"

    def test_respects_custom_firestore_collection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_required_env(monkeypatch)
        monkeypatch.setenv("GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION", "custom_docs")
        from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import (
            GcpVectorSearchProvider,
        )

        p = GcpVectorSearchProvider()
        assert p._firestore_collection == "custom_docs"


# ---------------------------------------------------------------------------
# provider_name
# ---------------------------------------------------------------------------


class TestProviderName:
    def test_provider_name(self, provider) -> None:
        assert provider.provider_name == "gcp-vector-search"


# ---------------------------------------------------------------------------
# create_collection
# ---------------------------------------------------------------------------


class TestCreateCollection:
    @pytest.mark.asyncio
    async def test_skips_removal_when_no_known_datapoints(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=False)
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        await provider.create_collection("col", metadata={"env": "prod"})

        provider._index.remove_datapoints.assert_not_called()
        set_call = provider._firestore.collection.return_value.document.return_value.set.call_args
        assert set_call.args[0] == {"metadata": {"env": "prod"}, "datapoint_ids": []}

    @pytest.mark.asyncio
    async def test_removes_known_datapoints_and_docs(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=True)
        meta_get.to_dict.return_value = {"datapoint_ids": ["a", "b"]}
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        await provider.create_collection("col")

        provider._index.remove_datapoints.assert_called_once_with(datapoint_ids=["a", "b"])
        assert provider._firestore.collection.return_value.document.return_value.delete.call_count == 2

    @pytest.mark.asyncio
    async def test_raises_vector_store_error_on_failure(self, wired_provider) -> None:
        provider = wired_provider
        provider._firestore.collection.side_effect = Exception("boom")

        from mcp_project_context_server.integrations.vectorstore.base import VectorStoreError

        with pytest.raises(VectorStoreError, match="Failed to create/clear collection"):
            await provider.create_collection("col")


# ---------------------------------------------------------------------------
# delete_collection
# ---------------------------------------------------------------------------


class TestDeleteCollection:
    @pytest.mark.asyncio
    async def test_removes_known_datapoints_and_meta(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=True)
        meta_get.to_dict.return_value = {"datapoint_ids": ["x"]}
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        await provider.delete_collection("col")

        provider._index.remove_datapoints.assert_called_once_with(datapoint_ids=["x"])
        provider._firestore.collection.return_value.document.return_value.delete.assert_called()

    @pytest.mark.asyncio
    async def test_silently_handles_exception(self, wired_provider) -> None:
        provider = wired_provider
        provider._firestore.collection.side_effect = Exception("connection refused")

        await provider.delete_collection("anything")  # must not raise


# ---------------------------------------------------------------------------
# upsert
# ---------------------------------------------------------------------------


class TestUpsert:
    @pytest.mark.asyncio
    async def test_noop_when_ids_empty(self, wired_provider) -> None:
        provider = wired_provider

        await provider.upsert("col", ids=[], embeddings=[], documents=[], metadatas=[])

        provider._index.upsert_datapoints.assert_not_called()

    @pytest.mark.asyncio
    async def test_upserts_datapoints_with_collection_restrict(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=False)
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        await provider.upsert(
            collection_name="col",
            ids=["id1", "id2"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["doc A", "doc B"],
            metadatas=[{"f": "1"}, {"f": "2"}],
        )

        datapoints = provider._index.upsert_datapoints.call_args.kwargs["datapoints"]
        assert datapoints == [
            {
                "datapoint_id": "id1",
                "feature_vector": [0.1, 0.2],
                "restricts": [{"namespace": "collection", "allow": ["col"]}],
            },
            {
                "datapoint_id": "id2",
                "feature_vector": [0.3, 0.4],
                "restricts": [{"namespace": "collection", "allow": ["col"]}],
            },
        ]

    @pytest.mark.asyncio
    async def test_writes_documents_and_metadata_to_firestore(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=False)
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get
        batch = provider._firestore.batch.return_value

        await provider.upsert(
            collection_name="col",
            ids=["id1"],
            embeddings=[[0.1]],
            documents=["doc A"],
            metadatas=[{"f": "1"}],
        )

        batch.set.assert_called_once()
        data = batch.set.call_args.args[1]
        assert data == {"collection": "col", "document": "doc A", "metadata": {"f": "1"}}
        batch.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_merges_datapoint_ids_into_existing_meta(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=True)
        meta_get.to_dict.return_value = {"metadata": {"env": "prod"}, "datapoint_ids": ["existing"]}
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        await provider.upsert(
            collection_name="col",
            ids=["new1"],
            embeddings=[[0.1]],
            documents=["doc"],
            metadatas=[{}],
        )

        meta_set_call = provider._firestore.collection.return_value.document.return_value.set.call_args
        assert meta_set_call.args[0] == {"metadata": {"env": "prod"}, "datapoint_ids": ["existing", "new1"]}

    @pytest.mark.asyncio
    async def test_raises_vector_store_error_on_failure(self, wired_provider) -> None:
        provider = wired_provider
        provider._index.upsert_datapoints.side_effect = Exception("SDK error")

        from mcp_project_context_server.integrations.vectorstore.base import VectorStoreError

        with pytest.raises(VectorStoreError, match="Upsert failed"):
            await provider.upsert("col", ids=["a"], embeddings=[[0.1]], documents=["d"], metadatas=[{}])


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------


class TestQuery:
    @pytest.mark.asyncio
    async def test_query_returns_query_result_with_correct_fields(self, wired_provider, mock_namespace) -> None:
        provider = wired_provider
        neighbor1 = MagicMock(id="id1", distance=0.9)
        neighbor2 = MagicMock(id="id2", distance=0.8)
        provider._endpoint.find_neighbors.return_value = [[neighbor1, neighbor2]]

        doc1 = MagicMock()
        doc1.get.return_value = MagicMock(exists=True, to_dict=lambda: {"document": "Doc 1", "metadata": {"file": "f1.md"}})
        doc2 = MagicMock()
        doc2.get.return_value = MagicMock(exists=True, to_dict=lambda: {"document": "Doc 2", "metadata": {"file": "f2.md"}})
        provider._firestore.collection.return_value.document.side_effect = lambda doc_id: {
            "id1": doc1,
            "id2": doc2,
        }[doc_id]

        result = await provider.query("col", [0.1, 0.2], n_results=2)

        assert result.ids == ["id1", "id2"]
        assert result.documents == ["Doc 1", "Doc 2"]
        assert result.metadatas == [{"file": "f1.md"}, {"file": "f2.md"}]
        assert result.distances == [0.9, 0.8]

        mock_namespace.assert_called_once_with(name="collection", allow_tokens=["col"])
        call_kwargs = provider._endpoint.find_neighbors.call_args.kwargs
        assert call_kwargs["deployed_index_id"] == "deployed-1"
        assert call_kwargs["queries"] == [[0.1, 0.2]]
        assert call_kwargs["num_neighbors"] == 2

    @pytest.mark.asyncio
    async def test_query_handles_empty_response(self, wired_provider, mock_namespace) -> None:
        provider = wired_provider
        provider._endpoint.find_neighbors.return_value = []

        result = await provider.query("col", [0.1], n_results=5)

        assert result.ids == []
        assert result.documents == []
        assert result.metadatas == []
        assert result.distances == []

    @pytest.mark.asyncio
    async def test_query_raises_vector_store_error_on_sdk_failure(self, wired_provider, mock_namespace) -> None:
        provider = wired_provider
        provider._endpoint.find_neighbors.side_effect = Exception("SDK error")

        from mcp_project_context_server.integrations.vectorstore.base import VectorStoreError

        with pytest.raises(VectorStoreError, match="Query failed"):
            await provider.query("col", [0.1])


# ---------------------------------------------------------------------------
# count
# ---------------------------------------------------------------------------


class TestCount:
    @pytest.mark.asyncio
    async def test_returns_known_datapoint_count(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=True)
        meta_get.to_dict.return_value = {"datapoint_ids": ["a", "b", "c"]}
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        assert await provider.count("col") == 3

    @pytest.mark.asyncio
    async def test_returns_zero_when_collection_missing(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=False)
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        assert await provider.count("col") == 0

    @pytest.mark.asyncio
    async def test_returns_zero_on_exception(self, wired_provider) -> None:
        provider = wired_provider
        provider._firestore.collection.side_effect = Exception("gone")

        assert await provider.count("col") == 0


# ---------------------------------------------------------------------------
# collection_exists
# ---------------------------------------------------------------------------


class TestCollectionExists:
    @pytest.mark.asyncio
    async def test_returns_true_when_meta_doc_found(self, wired_provider) -> None:
        provider = wired_provider
        provider._firestore.collection.return_value.document.return_value.get.return_value = MagicMock(exists=True)

        assert await provider.collection_exists("col") is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_meta_doc(self, wired_provider) -> None:
        provider = wired_provider
        provider._firestore.collection.return_value.document.return_value.get.return_value = MagicMock(exists=False)

        assert await provider.collection_exists("col") is False

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self, wired_provider) -> None:
        provider = wired_provider
        provider._firestore.collection.side_effect = Exception("gone")

        assert await provider.collection_exists("col") is False


# ---------------------------------------------------------------------------
# get_collection_metadata
# ---------------------------------------------------------------------------


class TestGetCollectionMetadata:
    @pytest.mark.asyncio
    async def test_returns_stored_metadata(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=True)
        meta_get.to_dict.return_value = {"metadata": {"env": "staging"}}
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        assert await provider.get_collection_metadata("col") == {"env": "staging"}

    @pytest.mark.asyncio
    async def test_returns_empty_dict_when_absent(self, wired_provider) -> None:
        provider = wired_provider
        meta_get = MagicMock(exists=False)
        provider._firestore.collection.return_value.document.return_value.get.return_value = meta_get

        assert await provider.get_collection_metadata("col") == {}

    @pytest.mark.asyncio
    async def test_returns_empty_dict_on_exception(self, wired_provider) -> None:
        provider = wired_provider
        provider._firestore.collection.side_effect = Exception("gone")

        assert await provider.get_collection_metadata("col") == {}


# ---------------------------------------------------------------------------
# reset_for_testing
# ---------------------------------------------------------------------------


class TestResetForTesting:
    def test_reset_sets_handles_to_none(self, wired_provider) -> None:
        provider = wired_provider
        provider.reset_for_testing()

        assert provider._index is None
        assert provider._endpoint is None
        assert provider._firestore is None
