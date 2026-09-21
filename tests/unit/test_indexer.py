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
    store.ensure_collection = AsyncMock()
    store.upsert = AsyncMock()
    store.list_ids = AsyncMock(return_value=[])
    store.delete_by_ids = AsyncMock()
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
        store.ensure_collection.assert_called_once()
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
        col_name = store.ensure_collection.call_args[0][0]
        assert col_name == "ctx_owner_repo"
        metadata = store.ensure_collection.call_args[1]["metadata"]
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

        col_name = store.ensure_collection.call_args[0][0]
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
        store.ensure_collection.assert_not_called()
        store.upsert.assert_not_called()
        store.delete_by_ids.assert_not_called()

    @pytest.mark.asyncio
    async def test_partial_chunk_embed_failure_aborts_without_writing_to_store(self, tmp_path):
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

        assert result.startswith("Error:")
        assert "timeout" in result
        assert "Section B" in result
        store.ensure_collection.assert_not_called()
        store.upsert.assert_not_called()
        store.delete_by_ids.assert_not_called()

    @pytest.mark.asyncio
    async def test_partial_failure_never_touches_previously_indexed_store(self, tmp_path):
        """Regression test: a transient embed failure on any subset of chunks
        must never destroy a previously-good collection (PROJECTCONTEXT-REINDEX-DATA-LOSS.md)."""
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        content = "## A\nFirst.\n\n## B\nSecond.\n\n## C\nThird.\n"
        (context_dir / "project.md").write_text(content, encoding="utf-8")

        embed_provider = _embed_provider()
        embed_provider.embed_chunk = AsyncMock(side_effect=[[0.1, 0.2], Exception("rate limited"), [0.3, 0.4]])

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=embed_provider),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
            patch("mcp_project_context_server.indexing.indexer._EMBED_CONCURRENCY", 1),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert result.startswith("Error:")
        store.ensure_collection.assert_not_called()
        store.upsert.assert_not_called()
        store.delete_by_ids.assert_not_called()

    @pytest.mark.asyncio
    async def test_zero_chunks_deletes_all_existing_ids(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "empty.md").write_text("", encoding="utf-8")

        store = _vector_store()
        stale_id = "old.md::Old Section::0-deadbeef"
        store.list_ids = AsyncMock(return_value=[stale_id])
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert "Indexed 0 chunks" in result
        store.ensure_collection.assert_called_once()
        store.delete_by_ids.assert_called_once_with(store.ensure_collection.call_args[0][0], [stale_id])
        store.upsert.assert_not_called()


class TestIncrementalDiff:
    """Content-addressed chunk IDs enable upsert-then-prune incremental indexing."""

    @pytest.mark.asyncio
    async def test_first_time_index_embeds_everything_and_deletes_nothing(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("## Section A\nHello.\n", encoding="utf-8")

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert "(1 embedded, 0 unchanged, 0 removed)" in result
        store.upsert.assert_called_once()
        store.delete_by_ids.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_op_reindex_skips_upsert_and_delete_but_refreshes_metadata(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("## Section A\nHello.\n", encoding="utf-8")

        first_store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            await run_index_pipeline(str(tmp_path), first_store)

        expected_ids = first_store.upsert.call_args.kwargs["ids"]

        second_store = _vector_store()
        second_store.list_ids = AsyncMock(return_value=expected_ids)
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), second_store)

        assert "(0 embedded, 1 unchanged, 0 removed)" in result
        second_store.upsert.assert_not_called()
        second_store.delete_by_ids.assert_not_called()
        second_store.ensure_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_partial_change_only_embeds_missing_chunk(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        content = "## Section A\nFirst.\n\n## Section B\nSecond.\n"
        (context_dir / "project.md").write_text(content, encoding="utf-8")

        first_store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            await run_index_pipeline(str(tmp_path), first_store)

        all_ids = first_store.upsert.call_args.kwargs["ids"]
        partial_ids = all_ids[:1]

        second_store = _vector_store()
        second_store.list_ids = AsyncMock(return_value=partial_ids)
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), second_store)

        assert "(1 embedded, 1 unchanged, 0 removed)" in result
        embedded_ids = second_store.upsert.call_args.kwargs["ids"]
        assert embedded_ids == [i for i in all_ids if i not in partial_ids]
        second_store.delete_by_ids.assert_not_called()

    @pytest.mark.asyncio
    async def test_stale_id_removed_is_deleted_without_reembedding_others(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("## Section A\nHello.\n", encoding="utf-8")

        store = _vector_store()
        stale_id = "old.md::Old Section::0-deadbeef"
        store.list_ids = AsyncMock(return_value=[stale_id])
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert "(1 embedded, 0 unchanged, 1 removed)" in result
        store.delete_by_ids.assert_called_once()
        assert store.delete_by_ids.call_args[0][1] == [stale_id]
        store.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_failure_on_incremental_run_only_attempts_missing_chunks(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        content = "## Section A\nFirst.\n\n## Section B\nSecond.\n"
        (context_dir / "project.md").write_text(content, encoding="utf-8")

        first_store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            await run_index_pipeline(str(tmp_path), first_store)

        all_ids = first_store.upsert.call_args.kwargs["ids"]
        existing_ids = all_ids[:1]

        embed_provider = _embed_provider()
        embed_provider.embed_chunk = AsyncMock(side_effect=Exception("rate limited"))

        second_store = _vector_store()
        second_store.list_ids = AsyncMock(return_value=existing_ids)
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=embed_provider),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), second_store)

        assert result.startswith("Error:")
        assert "failed to embed 1/1 chunks" in result
        second_store.ensure_collection.assert_not_called()
        second_store.upsert.assert_not_called()
        second_store.delete_by_ids.assert_not_called()

    @pytest.mark.asyncio
    async def test_duplicate_header_with_identical_content_dedups_to_one_chunk(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        content = "## Same\nHello.\n\n## Same\nHello.\n\n"
        (context_dir / "project.md").write_text(content, encoding="utf-8")

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
        ):
            result = await run_index_pipeline(str(tmp_path), store)

        assert "Indexed 1 chunks from 1 files" in result
        assert len(store.upsert.call_args.kwargs["ids"]) == 1

    @pytest.mark.asyncio
    async def test_segment_resets_per_section(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        para_a = "A" * 80
        para_b = "B" * 80
        content = f"## Section One\n{para_a}\n\n{para_b}\n\n## Section Two\n{para_a}\n\n{para_b}\n"
        (context_dir / "project.md").write_text(content, encoding="utf-8")

        store = _vector_store()
        with (
            patch("mcp_project_context_server.indexing.indexer.get_embedding_provider", return_value=_embed_provider()),
            patch("mcp_project_context_server.indexing.indexer.get_repository_provider", return_value=_repo_provider()),
            patch("mcp_project_context_server.indexing.indexer._MAX_CHUNK_SIZE", 100),
        ):
            await run_index_pipeline(str(tmp_path), store)

        ids = store.upsert.call_args.kwargs["ids"]
        section_one_first = [i for i in ids if i.startswith("project.md::Section One::0-")]
        section_two_first = [i for i in ids if i.startswith("project.md::Section Two::0-")]
        assert len(section_one_first) == 1
        assert len(section_two_first) == 1
