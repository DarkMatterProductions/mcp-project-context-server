"""Tests for VoyageEmbeddingProvider."""

import pytest

from mcp_project_context_server.integrations.embeddings.base import EmbeddingError
from mcp_project_context_server.integrations.embeddings.voyage.client import (
    VoyageEmbeddingProvider,
)


class TestVoyageEmbeddingProvider:
    def test_default_config(self, monkeypatch):
        """Provider uses default model when VOYAGE_EMBED_MODEL is not set."""
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")
        monkeypatch.delenv("VOYAGE_EMBED_MODEL", raising=False)
        provider = VoyageEmbeddingProvider()
        assert provider.provider_name == "voyage"
        assert provider.model_name == "voyage-code-3"
        assert provider.max_chars == 24_000

    def test_config_from_env(self, monkeypatch):
        """Provider reads model name from VOYAGE_EMBED_MODEL."""
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_EMBED_MODEL", "voyage-large-2")
        provider = VoyageEmbeddingProvider()
        assert provider.model_name == "voyage-large-2"
        assert provider._api_key == "test-key"

    def test_missing_api_key_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when VOYAGE_API_KEY is not set."""
        monkeypatch.delenv("VOYAGE_API_KEY", raising=False)
        with pytest.raises(EnvironmentError, match="VOYAGE_API_KEY"):
            VoyageEmbeddingProvider()

    def test_empty_api_key_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when VOYAGE_API_KEY is empty."""
        monkeypatch.setenv("VOYAGE_API_KEY", "")
        with pytest.raises(EnvironmentError, match="VOYAGE_API_KEY"):
            VoyageEmbeddingProvider()

    def test_max_chars(self, monkeypatch):
        """max_chars returns a positive integer."""
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")
        provider = VoyageEmbeddingProvider()
        assert provider.max_chars > 0

    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, monkeypatch, mocker):
        """embed() returns the embedding vector from the API response."""
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_result = mocker.MagicMock()
        mock_result.embeddings = [[0.1, 0.2, 0.3]]

        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed.return_value = mock_result

        mock_async_client_cls = mocker.MagicMock(return_value=mock_client_instance)

        mock_voyageai = mocker.MagicMock()
        mock_voyageai.AsyncClient = mock_async_client_cls

        mocker.patch.dict("sys.modules", {"voyageai": mock_voyageai})

        provider = VoyageEmbeddingProvider()
        result = await provider.embed("hello world")

        assert result == [0.1, 0.2, 0.3]
        mock_async_client_cls.assert_called_once_with(api_key="test-key")
        mock_client_instance.embed.assert_called_once_with(
            ["hello world"], model="voyage-code-3", input_type="document"
        )

    @pytest.mark.asyncio
    async def test_embed_raises_embedding_error_on_failure(self, monkeypatch, mocker):
        """embed() wraps exceptions in EmbeddingError."""
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")

        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed.side_effect = ConnectionError("refused")

        mock_voyageai = mocker.MagicMock()
        mock_voyageai.AsyncClient = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"voyageai": mock_voyageai})

        provider = VoyageEmbeddingProvider()
        with pytest.raises(EmbeddingError, match="Voyage AI embedding failed"):
            await provider.embed("test")

    @pytest.mark.asyncio
    async def test_embed_error_chains_original_exception(self, monkeypatch, mocker):
        """EmbeddingError.__cause__ is the original exception."""
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")
        original = RuntimeError("original error")

        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed.side_effect = original

        mock_voyageai = mocker.MagicMock()
        mock_voyageai.AsyncClient = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"voyageai": mock_voyageai})

        provider = VoyageEmbeddingProvider()
        with pytest.raises(EmbeddingError) as exc_info:
            await provider.embed("test")
        assert exc_info.value.__cause__ is original

    @pytest.mark.asyncio
    async def test_embed_uses_custom_model(self, monkeypatch, mocker):
        """embed() uses the model name from VOYAGE_EMBED_MODEL."""
        monkeypatch.setenv("VOYAGE_API_KEY", "test-key")
        monkeypatch.setenv("VOYAGE_EMBED_MODEL", "voyage-large-2")

        mock_result = mocker.MagicMock()
        mock_result.embeddings = [[0.4, 0.5]]

        mock_client_instance = mocker.AsyncMock()
        mock_client_instance.embed.return_value = mock_result

        mock_voyageai = mocker.MagicMock()
        mock_voyageai.AsyncClient = mocker.MagicMock(return_value=mock_client_instance)

        mocker.patch.dict("sys.modules", {"voyageai": mock_voyageai})

        provider = VoyageEmbeddingProvider()
        await provider.embed("text")

        mock_client_instance.embed.assert_called_once_with(["text"], model="voyage-large-2", input_type="document")
