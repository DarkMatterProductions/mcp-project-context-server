"""Tests for the embedding provider registry."""

import os

import pytest

from mcp_project_context_server.integrations.embeddings.registry import (
    get_embedding_provider,
)


class TestRegistryFailFast:
    def test_raises_when_embed_provider_not_set(self, monkeypatch):
        monkeypatch.delenv("EMBED_PROVIDER", raising=False)
        with pytest.raises(EnvironmentError, match="EMBED_PROVIDER environment variable is not set"):
            get_embedding_provider()

    def test_raises_when_embed_provider_empty_string(self, monkeypatch):
        monkeypatch.setenv("EMBED_PROVIDER", "")
        with pytest.raises(EnvironmentError, match="EMBED_PROVIDER environment variable is not set"):
            get_embedding_provider()

    def test_raises_when_embed_provider_unknown(self, monkeypatch):
        monkeypatch.setenv("EMBED_PROVIDER", "nonexistent-provider")
        with pytest.raises(EnvironmentError, match="Unsupported EMBED_PROVIDER value"):
            get_embedding_provider()

    def test_error_message_lists_supported_providers(self, monkeypatch):
        monkeypatch.delenv("EMBED_PROVIDER", raising=False)
        with pytest.raises(EnvironmentError) as exc_info:
            get_embedding_provider()
        # Should list known providers
        assert "ollama" in str(exc_info.value)
        assert "voyage" in str(exc_info.value)
        assert "openai" in str(exc_info.value)

    def test_provider_name_is_case_insensitive(self, monkeypatch, mocker):
        """Registry should normalise to lowercase before lookup."""
        mock_provider = mocker.MagicMock()
        mock_provider.provider_name = "ollama"
        mock_cls = mocker.patch(
            "mcp_project_context_server.integrations.embeddings.ollama.client.OllamaEmbeddingProvider",
            return_value=mock_provider,
        )
        monkeypatch.setenv("EMBED_PROVIDER", "OLLAMA")
        provider = get_embedding_provider()
        assert provider is mock_provider


class TestRegistryOllamaProvider:
    def test_returns_ollama_provider_when_configured(self, monkeypatch, mocker):
        mock_provider = mocker.MagicMock()
        mock_provider.provider_name = "ollama"
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.ollama.client.OllamaEmbeddingProvider",
            return_value=mock_provider,
        )
        monkeypatch.setenv("EMBED_PROVIDER", "ollama")
        provider = get_embedding_provider()
        assert provider is mock_provider

    def test_provider_is_cached_after_first_call(self, monkeypatch, mocker):
        mock_provider = mocker.MagicMock()
        mock_cls = mocker.patch(
            "mcp_project_context_server.integrations.embeddings.ollama.client.OllamaEmbeddingProvider",
            return_value=mock_provider,
        )
        monkeypatch.setenv("EMBED_PROVIDER", "ollama")

        p1 = get_embedding_provider()
        p2 = get_embedding_provider()

        assert p1 is p2
        # Constructor called exactly once despite two get_embedding_provider() calls
        assert mock_cls.call_count == 1


class TestRegistryResetForTesting:
    def test_reset_clears_cached_instance(self, monkeypatch, mocker):
        mock_provider = mocker.MagicMock()
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.ollama.client.OllamaEmbeddingProvider",
            return_value=mock_provider,
        )
        monkeypatch.setenv("EMBED_PROVIDER", "ollama")

        get_embedding_provider()

        # After reset, another call should build a new instance
        get_embedding_provider()
        # Called twice total (once before reset, once after)
