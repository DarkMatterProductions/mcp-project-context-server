"""Tests for the provider-agnostic indexing pipeline in indexing/indexer.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_project_context_server.indexing.indexer import run_index_pipeline
from mcp_project_context_server.integrations.repository.base import RepositoryError


def _embed_provider(chunk_size=1500):
    provider = MagicMock()
    provider.provider_name = "ollama"
    provider.model_name = "nomic-embed-text"
    provider.max_chars = chunk_size
    provider.embed_chunk = AsyncMock(return_value=[0.1, 0.2])
    return provider


def _vector_store():
    store = AsyncMock()
    store.provider_name = "chroma-local"
    store.create_collection = AsyncMock()
    store.upsert = AsyncMock()
    return store


def _repo_provider(name="local"):
    provider = AsyncMock()
    provider.provider_name = name
    return provider


class TestRunIndexPipelineLocal:
    """Local (non-remote) project_path — unchanged filesystem behavior."""

    @pytest.mark.asyncio
    async def test_no_context_dir_returns_message(self, tmp_path):
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path / "nonexistent"), _vector_store())

        assert "No .context/ directory found" in result

    @pytest.mark.asyncio
    async def test_indexes_local_files(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert "Indexed" in result
        store.create_collection.assert_called_once()
        store.upsert.assert_called_once()


class TestRunIndexPipelineRemote:
    """Remote project_path — fetched via the configured RepositoryProvider."""

    @pytest.mark.asyncio
    async def test_no_context_files_returns_message(self):
        repo_provider = _repo_provider("github")
        repo_provider.fetch_context_files = AsyncMock(return_value={})

        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=repo_provider),
        ):
            result = await run_index_pipeline("owner/repo", _vector_store())

        assert "No .context/ directory found in owner/repo" in result

    @pytest.mark.asyncio
    async def test_indexes_remote_files(self):
        repo_provider = _repo_provider("github")
        repo_provider.fetch_context_files = AsyncMock(return_value={"project.md": "# Project"})

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=repo_provider),
        ):
            result = await run_index_pipeline("owner/repo", store)

        assert "Indexed 1 chunks from 1 files" in result
        col_name = store.create_collection.call_args[0][0]
        assert col_name == "ctx_owner_repo"
        metadata = store.create_collection.call_args[1]["metadata"]
        assert metadata["repo_provider"] == "github"

    @pytest.mark.asyncio
    async def test_repository_error_is_reported(self):
        repo_provider = _repo_provider("github")
        repo_provider.fetch_context_files = AsyncMock(side_effect=RepositoryError("rate limited"))

        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=repo_provider),
        ):
            result = await run_index_pipeline("owner/repo", _vector_store())

        assert "Error accessing repository" in result
        assert "rate limited" in result

    @pytest.mark.asyncio
    async def test_url_form_resolves_to_same_collection_as_short_form(self):
        repo_provider = _repo_provider("github")
        repo_provider.fetch_context_files = AsyncMock(return_value={"project.md": "# Project"})

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=repo_provider),
        ):
            await run_index_pipeline("https://github.com/owner/repo", store)

        col_name = store.create_collection.call_args[0][0]
        assert col_name == "ctx_owner_repo"
