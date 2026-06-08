"""Tests for the provider-agnostic indexing/embedder.py module."""

import pytest

from mcp_project_context_server.integrations.embeddings.registry import reset_provider_for_testing


@pytest.fixture(autouse=True)
def reset_registry():
    reset_provider_for_testing()
    yield
    reset_provider_for_testing()


class TestEmbedChunk:
    @pytest.mark.asyncio
    async def test_delegates_to_provider(self, mocker):
        mock_provider = mocker.AsyncMock()
        mock_provider.embed.return_value = [0.5, 0.6]
        mock_provider.max_chars = 1000
        mocker.patch(
            "mcp_project_context_server.indexing.embedder.get_embedding_provider",
            return_value=mock_provider,
        )

        from mcp_project_context_server.indexing.embedder import embed_chunk

        result = await embed_chunk("test text")
        assert result == [0.5, 0.6]
        mock_provider.embed.assert_called_once_with("test text")

    @pytest.mark.asyncio
    async def test_propagates_provider_error(self, mocker):
        from mcp_project_context_server.integrations.embeddings.base import EmbeddingError

        mock_provider = mocker.AsyncMock()
        mock_provider.embed.side_effect = EmbeddingError("provider down")
        mock_provider.max_chars = 1000
        mocker.patch(
            "mcp_project_context_server.indexing.embedder.get_embedding_provider",
            return_value=mock_provider,
        )

        from mcp_project_context_server.indexing.embedder import embed_chunk

        with pytest.raises(EmbeddingError, match="provider down"):
            await embed_chunk("test text")


class TestGetMaxChars:
    def test_returns_provider_max_chars(self, mocker):
        mock_provider = mocker.MagicMock()
        mock_provider.max_chars = 32000
        mocker.patch(
            "mcp_project_context_server.indexing.embedder.get_embedding_provider",
            return_value=mock_provider,
        )

        from mcp_project_context_server.indexing.embedder import get_max_chars

        assert get_max_chars() == 32000
