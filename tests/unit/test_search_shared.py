"""Tests for the provenance-mismatch warning logic in tools/search_shared.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_project_context_server.integrations.vectorstore.base import QueryResult
from mcp_project_context_server.tools.search_shared import run_search


def _embed_provider(provider_name="ollama", model_name="nomic-embed-text"):
    provider = MagicMock()
    provider.provider_name = provider_name
    provider.model_name = model_name
    provider.embed_chunk = AsyncMock(return_value=[0.1, 0.2])
    return provider


def _vector_store(collection_metadata: dict, query_result: QueryResult | None = None):
    store = AsyncMock()
    store.provider_name = "chroma-local"
    store.collection_exists = AsyncMock(return_value=True)
    store.get_collection_metadata = AsyncMock(return_value=collection_metadata)
    store.query = AsyncMock(
        return_value=query_result
        or QueryResult(
            ids=["project.md::0"],
            documents=["hello world"],
            metadatas=[{"file": "project.md", "chunk": 0}],
            distances=[0.1],
        )
    )
    return store


def _repo_provider():
    provider = AsyncMock()
    provider.provider_name = "local"
    return provider


async def _run(tmp_path, store, embed_provider=None):
    context_dir = tmp_path / ".context"
    context_dir.mkdir(exist_ok=True)

    with (
        patch("mcp_project_context_server.tools.search_shared.validate_repo_access"),
        patch("mcp_project_context_server.tools.search_shared.get_repository_provider", return_value=_repo_provider()),
        patch("mcp_project_context_server.tools.search_shared.resolve_project_path", return_value=(str(tmp_path), False)),
        patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store),
        patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
            return_value=embed_provider or _embed_provider(),
        ),
    ):
        return await run_search(str(tmp_path), "why pgvector", 5)


class TestRunSearchProvenanceWarnings:
    @pytest.mark.asyncio
    async def test_no_mismatch_no_warning(self, tmp_path):
        store = _vector_store({"embed_provider": "ollama", "embed_model": "nomic-embed-text", "server_version": "1.0.0"})

        with patch("mcp_project_context_server.tools.search_shared.__version__", "1.0.0"):
            result = await _run(tmp_path, store)

        assert not result.content[0].text.startswith("⚠️")
        assert "warning" not in result.structured_content

    @pytest.mark.asyncio
    async def test_embed_provider_mismatch_warns(self, tmp_path):
        store = _vector_store({"embed_provider": "openai", "embed_model": "text-embedding-3-small", "server_version": "1.0.0"})

        with patch("mcp_project_context_server.tools.search_shared.__version__", "1.0.0"):
            result = await _run(tmp_path, store)

        assert "Provider mismatch detected" in result.content[0].text
        assert "openai/text-embedding-3-small" in result.content[0].text
        assert "ollama/nomic-embed-text" in result.content[0].text
        assert "Server version mismatch" not in result.content[0].text
        assert "Provider mismatch detected" in result.structured_content["warning"]

    @pytest.mark.asyncio
    async def test_server_version_mismatch_warns(self, tmp_path):
        store = _vector_store({"embed_provider": "ollama", "embed_model": "nomic-embed-text", "server_version": "0.9.0"})

        with patch("mcp_project_context_server.tools.search_shared.__version__", "1.0.0"):
            result = await _run(tmp_path, store)

        assert "Server version mismatch detected" in result.content[0].text
        assert "0.9.0" in result.content[0].text
        assert "1.0.0" in result.content[0].text
        assert "Provider mismatch detected" not in result.content[0].text

    @pytest.mark.asyncio
    async def test_both_provider_and_version_mismatch_warns_for_both(self, tmp_path):
        store = _vector_store({"embed_provider": "openai", "embed_model": "text-embedding-3-small", "server_version": "0.9.0"})

        with patch("mcp_project_context_server.tools.search_shared.__version__", "1.0.0"):
            result = await _run(tmp_path, store)

        assert "Provider mismatch detected" in result.content[0].text
        assert "Server version mismatch detected" in result.content[0].text

    @pytest.mark.asyncio
    async def test_missing_server_version_metadata_does_not_warn(self, tmp_path):
        store = _vector_store({"embed_provider": "ollama", "embed_model": "nomic-embed-text"})

        with patch("mcp_project_context_server.tools.search_shared.__version__", "1.0.0"):
            result = await _run(tmp_path, store)

        assert "Server version mismatch" not in result.content[0].text
