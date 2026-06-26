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

