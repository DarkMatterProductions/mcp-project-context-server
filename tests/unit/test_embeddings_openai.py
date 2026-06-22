"""Tests for OpenAIEmbeddingProvider."""

import pytest

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.openai.client import (
    OpenAIEmbeddingProvider,
)


class TestOpenAIEmbeddingProvider:
    def test_default_config(self, monkeypatch):
        """Provider uses default model when OPENAI_EMBED_MODEL is not set."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("OPENAI_EMBED_MODEL", raising=False)
        provider = OpenAIEmbeddingProvider()
        assert provider.provider_name == "openai"
        assert provider.model_name == "text-embedding-3-small"
        assert provider.max_chars == 24_000

    def test_config_from_env(self, monkeypatch):
        """Provider reads model name from OPENAI_EMBED_MODEL."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_EMBED_MODEL", "text-embedding-ada-002")
        provider = OpenAIEmbeddingProvider()
        assert provider.model_name == "text-embedding-ada-002"
        assert provider._api_key == "test-key"

    def test_missing_api_key_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when OPENAI_API_KEY is not set."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
            OpenAIEmbeddingProvider()

    def test_empty_api_key_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when OPENAI_API_KEY is empty."""
        monkeypatch.setenv("OPENAI_API_KEY", "")
        with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
            OpenAIEmbeddingProvider()

    def test_max_chars(self, monkeypatch):
        """max_chars returns a positive integer."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        provider = OpenAIEmbeddingProvider()
        assert provider.max_chars > 0

    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, monkeypatch, mocker):
        """embed() returns the embedding vector from the API response."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_embedding = mocker.MagicMock()
        mock_embedding.embedding = [0.1, 0.2, 0.3]

        mock_response = mocker.MagicMock()
        mock_response.data = [mock_embedding]

        mock_embeddings = mocker.AsyncMock()
        mock_embeddings.create.return_value = mock_response

        mock_client_instance = mocker.MagicMock()
        mock_client_instance.embeddings = mock_embeddings

        mock_async_openai_cls = mocker.MagicMock(return_value=mock_client_instance)

        mock_openai = mocker.MagicMock()
        mock_openai.AsyncOpenAI = mock_async_openai_cls

        mocker.patch.dict("sys.modules", {"openai": mock_openai})

        provider = OpenAIEmbeddingProvider()
        result = await provider.embed_chunk("hello world")

        assert result == [0.1, 0.2, 0.3]
        mock_async_openai_cls.assert_called_once_with(api_key="test-key")
        mock_embeddings.create.assert_called_once_with(model="text-embedding-3-small", input="hello world")

    @pytest.mark.asyncio
    async def test_embed_raises_embedding_error_on_failure(self, monkeypatch, mocker):
        """embed() wraps exceptions in EmbeddingError."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_embeddings = mocker.AsyncMock()
        mock_embeddings.create.side_effect = ConnectionError("refused")

        mock_client_instance = mocker.MagicMock()
        mock_client_instance.embeddings = mock_embeddings

        mock_openai = mocker.MagicMock()
        mock_openai.AsyncOpenAI = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"openai": mock_openai})

        provider = OpenAIEmbeddingProvider()
        with pytest.raises(EmbeddingError, match="OpenAI embedding failed"):
            await provider.embed_chunk("test")

    @pytest.mark.asyncio
    async def test_embed_error_chains_original_exception(self, monkeypatch, mocker):
        """EmbeddingError.__cause__ is the original exception."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        original = RuntimeError("original error")

        mock_embeddings = mocker.AsyncMock()
        mock_embeddings.create.side_effect = original

        mock_client_instance = mocker.MagicMock()
        mock_client_instance.embeddings = mock_embeddings

        mock_openai = mocker.MagicMock()
        mock_openai.AsyncOpenAI = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"openai": mock_openai})

        provider = OpenAIEmbeddingProvider()
        with pytest.raises(EmbeddingError) as exc_info:
            await provider.embed_chunk("test")
        assert exc_info.value.__cause__ is original

    @pytest.mark.asyncio
    async def test_embed_uses_custom_model(self, monkeypatch, mocker):
        """embed() uses the model name from OPENAI_EMBED_MODEL."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_EMBED_MODEL", "text-embedding-ada-002")

        mock_embedding = mocker.MagicMock()
        mock_embedding.embedding = [0.7, 0.8]

        mock_response = mocker.MagicMock()
        mock_response.data = [mock_embedding]

        mock_embeddings = mocker.AsyncMock()
        mock_embeddings.create.return_value = mock_response

        mock_client_instance = mocker.MagicMock()
        mock_client_instance.embeddings = mock_embeddings

        mock_openai = mocker.MagicMock()
        mock_openai.AsyncOpenAI = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"openai": mock_openai})

        provider = OpenAIEmbeddingProvider()
        await provider.embed_chunk("text")

        mock_embeddings.create.assert_called_once_with(model="text-embedding-ada-002", input="text")
