"""Tests for GoogleEmbeddingProvider."""

import pytest

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.google.client import (
    GoogleEmbeddingProvider,
)


def _patch_google_modules(mocker, mock_genai):
    """Patch sys.modules so that 'import google.generativeai as genai' resolves to mock_genai."""
    mock_google = mocker.MagicMock()
    mock_google.generativeai = mock_genai
    mocker.patch.dict(
        "sys.modules",
        {
            "google": mock_google,
            "google.generativeai": mock_genai,
        },
    )
    return mock_google


class TestGoogleEmbeddingProvider:
    def test_default_config(self, monkeypatch):
        """Provider uses default model when GOOGLE_EMBED_MODEL is not set."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.delenv("GOOGLE_EMBED_MODEL", raising=False)
        provider = GoogleEmbeddingProvider()
        assert provider.provider_name == "google"
        assert provider.model_name == "text-embedding-004"
        assert provider.max_chars == 24_000

    def test_config_from_env(self, monkeypatch):
        """Provider reads model name from GOOGLE_EMBED_MODEL."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.setenv("GOOGLE_EMBED_MODEL", "text-embedding-preview-0409")
        provider = GoogleEmbeddingProvider()
        assert provider.model_name == "text-embedding-preview-0409"
        assert provider._api_key == "test-key"

    def test_missing_api_key_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when GOOGLE_API_KEY is not set."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        with pytest.raises(EnvironmentError, match="GOOGLE_API_KEY"):
            GoogleEmbeddingProvider()

    def test_empty_api_key_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when GOOGLE_API_KEY is empty."""
        monkeypatch.setenv("GOOGLE_API_KEY", "")
        with pytest.raises(EnvironmentError, match="GOOGLE_API_KEY"):
            GoogleEmbeddingProvider()

    def test_max_chars(self, monkeypatch):
        """max_chars returns a positive integer."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        provider = GoogleEmbeddingProvider()
        assert provider.max_chars > 0

    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, monkeypatch, mocker):
        """embed() returns the embedding vector from the API response."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        mock_genai = mocker.MagicMock()
        _patch_google_modules(mocker, mock_genai)

        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.google.client.asyncio.to_thread",
            new=mocker.AsyncMock(return_value={"embedding": [0.1, 0.2, 0.3]}),
        )

        provider = GoogleEmbeddingProvider()
        result = await provider.embed("hello world")

        assert result == [0.1, 0.2, 0.3]

    @pytest.mark.asyncio
    async def test_embed_calls_configure_and_embed_content(self, monkeypatch, mocker):
        """embed() calls genai.configure() and passes genai.embed_content with correct args to to_thread."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        mock_genai = mocker.MagicMock()
        _patch_google_modules(mocker, mock_genai)

        mock_to_thread = mocker.AsyncMock(return_value={"embedding": [0.4, 0.5, 0.6]})
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.google.client.asyncio.to_thread",
            mock_to_thread,
        )

        provider = GoogleEmbeddingProvider()
        result = await provider.embed("hello world")

        mock_genai.configure.assert_called_once_with(api_key="test-key")
        # to_thread(genai.embed_content, model=..., content=...)
        mock_to_thread.assert_called_once()
        call_kwargs = mock_to_thread.call_args.kwargs
        assert call_kwargs.get("model") == "text-embedding-004"
        assert call_kwargs.get("content") == "hello world"
        assert result == [0.4, 0.5, 0.6]

    @pytest.mark.asyncio
    async def test_embed_raises_embedding_error_on_failure(self, monkeypatch, mocker):
        """embed() wraps exceptions in EmbeddingError."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        mock_genai = mocker.MagicMock()
        _patch_google_modules(mocker, mock_genai)

        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.google.client.asyncio.to_thread",
            new=mocker.AsyncMock(side_effect=ConnectionError("refused")),
        )

        provider = GoogleEmbeddingProvider()
        with pytest.raises(EmbeddingError, match="Google embedding failed"):
            await provider.embed("test")

    @pytest.mark.asyncio
    async def test_embed_error_chains_original_exception(self, monkeypatch, mocker):
        """EmbeddingError.__cause__ is the original exception."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        original = RuntimeError("original error")

        mock_genai = mocker.MagicMock()
        _patch_google_modules(mocker, mock_genai)

        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.google.client.asyncio.to_thread",
            new=mocker.AsyncMock(side_effect=original),
        )

        provider = GoogleEmbeddingProvider()
        with pytest.raises(EmbeddingError) as exc_info:
            await provider.embed("test")
        assert exc_info.value.__cause__ is original

    @pytest.mark.asyncio
    async def test_embed_uses_custom_model(self, monkeypatch, mocker):
        """embed() uses the model name from GOOGLE_EMBED_MODEL."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.setenv("GOOGLE_EMBED_MODEL", "text-embedding-preview-0409")

        mock_genai = mocker.MagicMock()
        _patch_google_modules(mocker, mock_genai)

        mock_to_thread = mocker.AsyncMock(return_value={"embedding": [0.9]})
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.google.client.asyncio.to_thread",
            mock_to_thread,
        )

        provider = GoogleEmbeddingProvider()
        await provider.embed("text")

        mock_to_thread.assert_called_once()
        call_kwargs = mock_to_thread.call_args.kwargs
        assert call_kwargs.get("model") == "text-embedding-preview-0409"
        assert call_kwargs.get("content") == "text"
