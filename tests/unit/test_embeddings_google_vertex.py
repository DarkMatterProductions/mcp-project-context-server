"""Tests for GoogleVertexEmbeddingProvider."""

import pytest

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.vertexai.client import (
    GoogleVertexEmbeddingProvider,
)


class TestGoogleVertexEmbeddingProvider:
    def test_default_config(self, monkeypatch):
        """Provider uses default model when GOOGLE_VERTEX_EMBED_MODEL is not set."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "us-central1")
        monkeypatch.delenv("GOOGLE_VERTEX_EMBED_MODEL", raising=False)
        provider = GoogleVertexEmbeddingProvider()
        assert provider.provider_name == "vertexai"
        assert provider.model_name == "text-embedding-004"
        assert provider.max_chars == 24_000

    def test_config_from_env(self, monkeypatch):
        """Provider reads all config from environment variables."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "europe-west1")
        monkeypatch.setenv("GOOGLE_VERTEX_EMBED_MODEL", "text-multilingual-embedding-002")
        provider = GoogleVertexEmbeddingProvider()
        assert provider.model_name == "text-multilingual-embedding-002"
        assert provider._project == "my-project"
        assert provider._location == "europe-west1"

    def test_missing_project_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when GOOGLE_VERTEX_PROJECT is not set."""
        monkeypatch.delenv("GOOGLE_VERTEX_PROJECT", raising=False)
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "us-central1")
        with pytest.raises(EnvironmentError, match="GOOGLE_VERTEX_PROJECT"):
            GoogleVertexEmbeddingProvider()

    def test_empty_project_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when GOOGLE_VERTEX_PROJECT is empty."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "us-central1")
        with pytest.raises(EnvironmentError, match="GOOGLE_VERTEX_PROJECT"):
            GoogleVertexEmbeddingProvider()

    def test_missing_location_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when GOOGLE_VERTEX_LOCATION is not set."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.delenv("GOOGLE_VERTEX_LOCATION", raising=False)
        with pytest.raises(EnvironmentError, match="GOOGLE_VERTEX_LOCATION"):
            GoogleVertexEmbeddingProvider()

    def test_empty_location_raises_environment_error(self, monkeypatch):
        """EnvironmentError is raised when GOOGLE_VERTEX_LOCATION is empty."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "")
        with pytest.raises(EnvironmentError, match="GOOGLE_VERTEX_LOCATION"):
            GoogleVertexEmbeddingProvider()

    def test_max_chars(self, monkeypatch):
        """max_chars returns a positive integer."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "us-central1")
        provider = GoogleVertexEmbeddingProvider()
        assert provider.max_chars > 0

    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, monkeypatch, mocker):
        """embed() returns the embedding vector from the SDK response."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "us-central1")

        mock_embedding = mocker.MagicMock()
        mock_embedding.values = [0.1, 0.2, 0.3]

        mock_model_instance = mocker.MagicMock()
        mock_model_instance.get_embeddings.return_value = [mock_embedding]

        mock_text_embedding_model = mocker.MagicMock()
        mock_text_embedding_model.from_pretrained.return_value = mock_model_instance

        mock_vertexai = mocker.MagicMock()
        mock_language_models = mocker.MagicMock()
        mock_language_models.TextEmbeddingModel = mock_text_embedding_model

        mocker.patch.dict(
            "sys.modules",
            {
                "vertexai": mock_vertexai,
                "vertexai.language_models": mock_language_models,
            },
        )

        async def fake_to_thread(fn, *args, **kwargs):
            return fn(*args, **kwargs)

        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.vertexai.client.asyncio.to_thread",
            side_effect=fake_to_thread,
        )

        provider = GoogleVertexEmbeddingProvider()
        result = await provider.embed("hello world")

        assert result == [0.1, 0.2, 0.3]
        mock_vertexai.init.assert_called_once_with(project="my-project", location="us-central1")
        mock_text_embedding_model.from_pretrained.assert_called_once_with("text-embedding-004")
        mock_model_instance.get_embeddings.assert_called_once_with(["hello world"])

    @pytest.mark.asyncio
    async def test_embed_raises_embedding_error_on_failure(self, monkeypatch, mocker):
        """embed() wraps exceptions in EmbeddingError."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "us-central1")

        mock_vertexai = mocker.MagicMock()
        mock_language_models = mocker.MagicMock()

        mocker.patch.dict(
            "sys.modules",
            {
                "vertexai": mock_vertexai,
                "vertexai.language_models": mock_language_models,
            },
        )

        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.vertexai.client.asyncio.to_thread",
            new=mocker.AsyncMock(side_effect=ConnectionError("refused")),
        )

        provider = GoogleVertexEmbeddingProvider()
        with pytest.raises(EmbeddingError, match="Google Vertex AI embedding failed"):
            await provider.embed("test")

    @pytest.mark.asyncio
    async def test_embed_error_chains_original_exception(self, monkeypatch, mocker):
        """EmbeddingError.__cause__ is the original exception."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "us-central1")
        original = RuntimeError("original error")

        mock_vertexai = mocker.MagicMock()
        mock_language_models = mocker.MagicMock()

        mocker.patch.dict(
            "sys.modules",
            {
                "vertexai": mock_vertexai,
                "vertexai.language_models": mock_language_models,
            },
        )

        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.vertexai.client.asyncio.to_thread",
            new=mocker.AsyncMock(side_effect=original),
        )

        provider = GoogleVertexEmbeddingProvider()
        with pytest.raises(EmbeddingError) as exc_info:
            await provider.embed("test")
        assert exc_info.value.__cause__ is original

    @pytest.mark.asyncio
    async def test_embed_uses_custom_model(self, monkeypatch, mocker):
        """embed() uses the model name from GOOGLE_VERTEX_EMBED_MODEL."""
        monkeypatch.setenv("GOOGLE_VERTEX_PROJECT", "my-project")
        monkeypatch.setenv("GOOGLE_VERTEX_LOCATION", "us-central1")
        monkeypatch.setenv("GOOGLE_VERTEX_EMBED_MODEL", "text-multilingual-embedding-002")

        mock_embedding = mocker.MagicMock()
        mock_embedding.values = [0.9]

        mock_model_instance = mocker.MagicMock()
        mock_model_instance.get_embeddings.return_value = [mock_embedding]

        mock_text_embedding_model = mocker.MagicMock()
        mock_text_embedding_model.from_pretrained.return_value = mock_model_instance

        mock_vertexai = mocker.MagicMock()
        mock_language_models = mocker.MagicMock()
        mock_language_models.TextEmbeddingModel = mock_text_embedding_model

        mocker.patch.dict(
            "sys.modules",
            {
                "vertexai": mock_vertexai,
                "vertexai.language_models": mock_language_models,
            },
        )

        async def fake_to_thread(fn, *args, **kwargs):
            return fn(*args, **kwargs)

        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.vertexai.client.asyncio.to_thread",
            side_effect=fake_to_thread,
        )

        provider = GoogleVertexEmbeddingProvider()
        await provider.embed("text")

        mock_text_embedding_model.from_pretrained.assert_called_once_with("text-multilingual-embedding-002")
