"""Tests for OllamaEmbeddingProvider."""

import pytest

from mcp_project_context_server.integrations.embeddings.base import EmbeddingError
from mcp_project_context_server.integrations.embeddings.ollama.client import (
    OllamaEmbeddingProvider,
)


class TestOllamaEmbeddingProvider:
    def test_default_config(self, monkeypatch):
        monkeypatch.delenv("OLLAMA_HOST", raising=False)
        monkeypatch.delenv("OLLAMA_EMBED_MODEL", raising=False)
        monkeypatch.delenv("EMBED_MODEL", raising=False)
        provider = OllamaEmbeddingProvider()
        assert provider.provider_name == "ollama"
        assert provider.model_name == "nomic-embed-text"
        assert provider.max_chars > 0

    def test_config_from_env(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_HOST", "http://custom:11434")
        monkeypatch.setenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
        provider = OllamaEmbeddingProvider()
        assert provider.model_name == "mxbai-embed-large"
        assert provider._host == "http://custom:11434"

    def test_legacy_embed_model_env_var(self, monkeypatch):
        """EMBED_MODEL (legacy) should be respected when OLLAMA_EMBED_MODEL is absent."""
        monkeypatch.delenv("OLLAMA_EMBED_MODEL", raising=False)
        monkeypatch.setenv("EMBED_MODEL", "legacy-model")
        provider = OllamaEmbeddingProvider()
        assert provider.model_name == "legacy-model"

    def test_ollama_embed_model_takes_precedence_over_embed_model(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_EMBED_MODEL", "preferred-model")
        monkeypatch.setenv("EMBED_MODEL", "fallback-model")
        provider = OllamaEmbeddingProvider()
        assert provider.model_name == "preferred-model"

    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]
        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed.return_value = mock_response
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.ollama.client.ollama.AsyncClient",
            return_value=mock_client_instance,
        )

        provider = OllamaEmbeddingProvider()
        result = await provider.embed("hello world")

        assert result == [0.1, 0.2, 0.3]
        mock_client_instance.embed.assert_called_once_with(model=provider.model_name, input="hello world")

    @pytest.mark.asyncio
    async def test_embed_raises_embedding_error_on_failure(self, mocker):
        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed.side_effect = ConnectionError("refused")
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.ollama.client.ollama.AsyncClient",
            return_value=mock_client_instance,
        )

        provider = OllamaEmbeddingProvider()
        with pytest.raises(EmbeddingError, match="Ollama embedding failed"):
            await provider.embed("test")

    @pytest.mark.asyncio
    async def test_embed_error_chains_original_exception(self, mocker):
        original = RuntimeError("original error")
        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed.side_effect = original
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.ollama.client.ollama.AsyncClient",
            return_value=mock_client_instance,
        )

        provider = OllamaEmbeddingProvider()
        with pytest.raises(EmbeddingError) as exc_info:
            await provider.embed("test")
        assert exc_info.value.__cause__ is original
