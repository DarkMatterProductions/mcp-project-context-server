"""Tests for the provider-agnostic indexing/embedder.py module."""

import pytest

from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider
from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from tests.shared import EMBEDDING_PROVIDER


def _provider_param(provider_name: str) -> pytest.param:
    """Return a pytest.param for *provider_name*, marked skip when opted out."""
    env_key = f"SKIP_EMBED_PROVIDER_{provider_name.upper().replace('-', '_')}"
    if os.getenv(env_key):
        return pytest.param(provider_name, marks=pytest.mark.skip(reason=f"{env_key} is set"))
    return pytest.param(provider_name)



class TestEmbedChunk:
    @pytest.mark.asyncio
    async def test_delegates_to_provider(self, mocker):
        mock_provider = mocker.AsyncMock(spec=EmbeddingProvider)
        mock_provider.embed_chunk.return_value = [0.5, 0.6]
        mock_provider.max_chars = 1000
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.registry.get_embedding_provider",
            return_value=mock_provider,
        )

        provider = get_embedding_provider()
        result = await provider.embed_chunk("test text")
        assert result == [0.5, 0.6]
        mock_provider.embed_chunk.assert_called_once_with("test text")

    @pytest.mark.asyncio
    async def test_propagates_provider_error(self, mocker):
        from mcp_project_context_server.exceptions import EmbeddingError

        mock_provider = mocker.AsyncMock()
        mock_provider.embed_chunk.side_effect = EmbeddingError("provider down")
        mock_provider.max_chars = 1000
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.registry.get_embedding_provider",
            return_value=mock_provider,
        )

        from embedder import embed_chunk

        with pytest.raises(EmbeddingError, match="provider down"):
            await embed_chunk("test text")


class TestGetMaxChars:
    def test_returns_provider_max_chars(self, mocker):
        mock_provider = mocker.MagicMock()
        mock_provider.max_chars = 32000
        mocker.patch(
            "mcp_project_context_server.integrations.embeddings.registry.get_embedding_provider",
            return_value=mock_provider,
        )

        from embedder import get_max_chars

        assert get_max_chars() == 32000
