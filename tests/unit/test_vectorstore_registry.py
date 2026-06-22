"""Tests for integrations/vectorstore/registry.py — get_vector_store(), reset_provider_for_testing()."""

import pytest
from pytest_mock import MockerFixture

from mcp_project_context_server.integrations.vectorstore.registry import (
    get_vector_store,
)

_CHROMA_LOCAL_CLS = (
    "mcp_project_context_server.integrations.vectorstore.chroma_local.client.ChromaLocalVectorStoreProvider"
)
_CHROMA_HTTP_CLS = (
    "mcp_project_context_server.integrations.vectorstore.chroma_http.client.ChromaHttpVectorStoreProvider"
)
_PGVECTOR_CLS = "mcp_project_context_server.integrations.vectorstore.pgvector.client.PgVectorStoreProvider"


class TestGetVectorStore:
    def test_returns_chroma_local_by_default(self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
        monkeypatch.delenv("VECTOR_STORE_PROVIDER", raising=False)
        mock_cls = mocker.patch(_CHROMA_LOCAL_CLS)
        store = get_vector_store()
        mock_cls.assert_called_once()
        assert store is mock_cls.return_value

    def test_returns_chroma_local_when_env_is_chroma_local(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        monkeypatch.setenv("VECTOR_STORE_PROVIDER", "chroma-local")
        mock_cls = mocker.patch(_CHROMA_LOCAL_CLS)
        store = get_vector_store()
        mock_cls.assert_called_once()
        assert store is mock_cls.return_value

    def test_returns_chroma_http_when_env_is_chroma_http(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        monkeypatch.setenv("VECTOR_STORE_PROVIDER", "chroma-http")
        mock_cls = mocker.patch(_CHROMA_HTTP_CLS)
        store = get_vector_store()
        mock_cls.assert_called_once()
        assert store is mock_cls.return_value

    def test_returns_pgvector_when_env_is_pgvector(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        monkeypatch.setenv("VECTOR_STORE_PROVIDER", "pgvector")
        mock_cls = mocker.patch(_PGVECTOR_CLS)
        store = get_vector_store()
        mock_cls.assert_called_once()
        assert store is mock_cls.return_value

    def test_raises_environment_error_for_unknown_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTOR_STORE_PROVIDER", "totally-unknown")
        with pytest.raises(EnvironmentError, match="Unsupported VECTOR_STORE_PROVIDER"):
            get_vector_store()

    def test_provider_is_cached_after_first_call(self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
        monkeypatch.delenv("VECTOR_STORE_PROVIDER", raising=False)
        mock_cls = mocker.patch(_CHROMA_LOCAL_CLS)
        store1 = get_vector_store()
        store2 = get_vector_store()
        assert store1 is store2
        mock_cls.assert_called_once()  # constructor invoked only once

    def test_reset_provider_for_testing_clears_cached_instance(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        monkeypatch.delenv("VECTOR_STORE_PROVIDER", raising=False)
        mock_cls = mocker.patch(_CHROMA_LOCAL_CLS)

        instance1 = mocker.MagicMock(name="inst1")
        instance2 = mocker.MagicMock(name="inst2")
        mock_cls.side_effect = [instance1, instance2]

        store1 = get_vector_store()
        reset_provider_for_testing()
        store2 = get_vector_store()

        assert mock_cls.call_count == 2  # two separate instantiations
        assert store1 is instance1
        assert store2 is instance2
        assert store1 is not store2
