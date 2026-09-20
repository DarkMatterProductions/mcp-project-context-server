"""Tests for the provider-agnostic indexing pipeline in indexing/indexer.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_project_context_server.helpers.context_files import hash_content
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


class TestHeadingBoundaryChunking:
    """ADR-00007: one chunk per top-level (##) section, with section/section_sha512 metadata."""

    @pytest.mark.asyncio
    async def test_one_chunk_per_section_with_metadata(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        content = "# ADR-00001: Title\n\n## Status\nAccepted\n\n## Context\nSome context.\n"
        (context_dir / "decisions" / "ADR-00001-title.md").parent.mkdir(parents=True)
        (context_dir / "decisions" / "ADR-00001-title.md").write_text(content, encoding="utf-8")

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert "Indexed 3 chunks from 1 files" in result
        metadatas = store.upsert.call_args.kwargs["metadatas"]
        sections = {m["section"] for m in metadatas}
        assert sections == {"ADR-00001: Title", "Status", "Context"}
        for meta in metadatas:
            assert meta["section_sha512"]

    @pytest.mark.asyncio
    async def test_oversized_section_sub_chunks_share_section_metadata(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        para_a = "A" * 80
        para_b = "B" * 80
        content = f"## Context\n{para_a}\n\n{para_b}\n"
        (context_dir / "project.md").write_text(content, encoding="utf-8")

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
            patch("mcp_project_context_server.indexing.indexer._MAX_CHUNK_SIZE", 100),
        ):
            await run_index_pipeline(str(tmp_path), store)

        metadatas = store.upsert.call_args.kwargs["metadatas"]
        assert len(metadatas) > 1
        section_names = {m["section"] for m in metadatas}
        section_hashes = {m["section_sha512"] for m in metadatas}
        assert section_names == {"Context"}
        assert section_hashes == {hash_content(content)}
        chunk_indices = [m["chunk"] for m in metadatas]
        assert chunk_indices == list(range(len(metadatas)))

    @pytest.mark.asyncio
    async def test_chunk_size_env_override_changes_split_point(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        para_a = "A" * 80
        para_b = "B" * 80
        content = f"## Context\n{para_a}\n\n{para_b}\n"
        (context_dir / "project.md").write_text(content, encoding="utf-8")

        store_small = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
            patch("mcp_project_context_server.indexing.indexer._MAX_CHUNK_SIZE", 100),
        ):
            await run_index_pipeline(str(tmp_path), store_small)

        store_large = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
            patch("mcp_project_context_server.indexing.indexer._MAX_CHUNK_SIZE", 1500),
        ):
            await run_index_pipeline(str(tmp_path), store_large)

        small_count = len(store_small.upsert.call_args.kwargs["metadatas"])
        large_count = len(store_large.upsert.call_args.kwargs["metadatas"])
        assert small_count > large_count == 1


class TestEmbedFailureHandling:
    """Embed-call failures must be surfaced explicitly, never silently dropped."""

    @pytest.mark.asyncio
    async def test_all_chunks_fail_to_embed_returns_explicit_error(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        embed_provider = _embed_provider()
        embed_provider.embed_chunk = AsyncMock(side_effect=Exception("connection refused"))

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=embed_provider),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert result.startswith("Error:")
        assert "connection refused" in result
        store.upsert.assert_not_called()

    @pytest.mark.asyncio
    async def test_partial_chunk_embed_failure_reports_count(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        content = "## Section A\nFirst.\n\n## Section B\nSecond.\n"
        (context_dir / "project.md").write_text(content, encoding="utf-8")

        embed_provider = _embed_provider()
        embed_provider.embed_chunk = AsyncMock(side_effect=[[0.1, 0.2], Exception("timeout")])

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=embed_provider),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
            patch("mcp_project_context_server.indexing.indexer._EMBED_CONCURRENCY", 1),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert "Indexed 1 chunks from 1 files" in result
        assert "1 chunks failed to embed" in result
        store.upsert.assert_called_once()
        assert len(store.upsert.call_args.kwargs["ids"]) == 1
