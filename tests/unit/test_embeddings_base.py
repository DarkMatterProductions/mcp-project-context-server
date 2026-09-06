"""Tests for the EmbeddingProvider Protocol and EmbeddingError."""

import pytest

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import (
    EmbeddingProvider,
)


class _ConcreteProvider:
    """Minimal concrete class that satisfies the EmbeddingProvider Protocol."""

    @property
    def provider_name(self) -> str:
        return "test"

    @property
    def model_name(self) -> str:
        return "test-model"

    @property
    def max_chars(self) -> int:
        return 1000

    async def embed_chunk(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class _IncompleteProvider:
    """Class that does NOT implement all Protocol properties."""

    @property
    def provider_name(self) -> str:
        return "incomplete"

    # Missing: model_name, max_chars, embed


class TestEmbeddingProviderProtocol:
    def test_concrete_provider_satisfies_protocol(self):
        provider = _ConcreteProvider()
        assert isinstance(provider, EmbeddingProvider)

    def test_incomplete_provider_does_not_satisfy_protocol(self):
        provider = _IncompleteProvider()
        assert not isinstance(provider, EmbeddingProvider)

    def test_protocol_properties_accessible(self):
        provider = _ConcreteProvider()
        assert provider.provider_name == "test"
        assert provider.model_name == "test-model"
        assert provider.max_chars == 1000

    @pytest.mark.asyncio
    async def test_protocol_embed_returns_vector(self):
        provider = _ConcreteProvider()
        result = await provider.embed_chunk("hello")
        assert result == [0.1, 0.2, 0.3]


class TestEmbeddingError:
    def test_embedding_error_is_exception(self):
        err = EmbeddingError("something went wrong")
        assert isinstance(err, Exception)
        assert str(err) == "something went wrong"

    def test_embedding_error_can_chain_cause(self):
        cause = ValueError("root cause")
        err = EmbeddingError("wrapper")
        err.__cause__ = cause
        assert err.__cause__ is cause
