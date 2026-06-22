"""Tests for CohereEmbeddingProvider."""

import pytest

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.cohere.client import (
    CohereEmbeddingProvider,
)


class TestCohereEmbeddingProvider:
    def test_default_config(self, monkeypatch):
        """Provider uses default model when COHERE_EMBED_MODEL is not set."""
        monkeypatch.setenv("COHERE_API_KEY", "test-key")
        monkeypatch.delenv("COHERE_EMBED_MODEL", raising=False)
        provider = CohereEmbeddingProvider()
        assert provider.provider_name == "cohere"
        assert provider.model_name == "embed-english-v3.0"
        assert provider.max_chars == 20_000

    def test_config_from_env(self, monkeypatch):
        """Provider reads model name from COHERE_EMBED_MODEL."""
        monkeypatch.setenv("COHERE_API_KEY", "test-key")
        monkeypatch.setenv("COHERE_EMBED_MODEL", "embed-multilingual-v3.0")
        provider = CohereEmbeddingProvider()
        assert provider.model_name == "embed-multilingual-v3.0"
        assert provider._api_key == "test-key"

    def test_missing_api_key_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when COHERE_API_KEY is not set."""
        monkeypatch.delenv("COHERE_API_KEY", raising=False)
        with pytest.raises(EnvironmentError, match="COHERE_API_KEY"):
            CohereEmbeddingProvider()

    def test_empty_api_key_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when COHERE_API_KEY is empty."""
        monkeypatch.setenv("COHERE_API_KEY", "")
        with pytest.raises(EnvironmentError, match="COHERE_API_KEY"):
            CohereEmbeddingProvider()

    def test_max_chars(self, monkeypatch):
        """max_chars returns a positive integer."""
        monkeypatch.setenv("COHERE_API_KEY", "test-key")
        provider = CohereEmbeddingProvider()
        assert provider.max_chars > 0

    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, monkeypatch, mocker):
        """embed() returns the embedding vector from the API response."""
        monkeypatch.setenv("COHERE_API_KEY", "test-key")

        mock_embeddings_obj = mocker.MagicMock()
        mock_embeddings_obj.float_ = [[0.1, 0.2, 0.3]]

        mock_response = mocker.MagicMock()
        mock_response.embeddings = mock_embeddings_obj

        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed_chunk.return_value = mock_response

        mock_async_client_cls = mocker.MagicMock(return_value=mock_client_instance)

        mock_cohere = mocker.MagicMock()
        mock_cohere.AsyncClientV2 = mock_async_client_cls

        mocker.patch.dict("sys.modules", {"cohere": mock_cohere})

        provider = CohereEmbeddingProvider()
        result = await provider.embed_chunk("hello world")

        assert result == [0.1, 0.2, 0.3]
        mock_async_client_cls.assert_called_once_with(api_key="test-key")
        mock_client_instance.embed_chunk.assert_called_once_with(
            texts=["hello world"],
            model="embed-english-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        )

    @pytest.mark.asyncio
    async def test_embed_raises_embedding_error_on_failure(self, monkeypatch, mocker):
        """embed() wraps exceptions in EmbeddingError."""
        monkeypatch.setenv("COHERE_API_KEY", "test-key")

        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed_chunk.side_effect = ConnectionError("refused")

        mock_cohere = mocker.MagicMock()
        mock_cohere.AsyncClientV2 = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"cohere": mock_cohere})

        provider = CohereEmbeddingProvider()
        with pytest.raises(EmbeddingError, match="Cohere embedding failed"):
            await provider.embed_chunk("test")

    @pytest.mark.asyncio
    async def test_embed_error_chains_original_exception(self, monkeypatch, mocker):
        """EmbeddingError.__cause__ is the original exception."""
        monkeypatch.setenv("COHERE_API_KEY", "test-key")
        original = RuntimeError("original error")

        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed_chunk.side_effect = original

        mock_cohere = mocker.MagicMock()
        mock_cohere.AsyncClientV2 = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"cohere": mock_cohere})

        provider = CohereEmbeddingProvider()
        with pytest.raises(EmbeddingError) as exc_info:
            await provider.embed_chunk("test")
        assert exc_info.value.__cause__ is original

    @pytest.mark.asyncio
    async def test_embed_uses_custom_model(self, monkeypatch, mocker):
        """embed() uses the model name from COHERE_EMBED_MODEL."""
        monkeypatch.setenv("COHERE_API_KEY", "test-key")
        monkeypatch.setenv("COHERE_EMBED_MODEL", "embed-multilingual-v3.0")

        mock_embeddings_obj = mocker.MagicMock()
        mock_embeddings_obj.float_ = [[0.4, 0.5]]

        mock_response = mocker.MagicMock()
        mock_response.embeddings = mock_embeddings_obj

        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed_chunk.return_value = mock_response

        mock_cohere = mocker.MagicMock()
        mock_cohere.AsyncClientV2 = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"cohere": mock_cohere})

        provider = CohereEmbeddingProvider()
        await provider.embed_chunk("text")

        mock_client_instance.embed_chunk.assert_called_once_with(
            texts=["text"],
            model="embed-multilingual-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        )
