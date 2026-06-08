"""Tests for the search_project_context tool (Phase 5/6 vector store registry interface)."""

import pytest

from mcp_project_context_server.integrations.embeddings.registry import reset_provider_for_testing
from mcp_project_context_server.integrations.vectorstore.base import QueryResult, VectorStoreError
from mcp_project_context_server.integrations.vectorstore.registry import (
    reset_provider_for_testing as reset_vs,
)
from mcp_project_context_server.tools.search_context import handle


@pytest.fixture(autouse=True)
def reset_registries():
    reset_provider_for_testing()
    reset_vs()
    yield
    reset_provider_for_testing()
    reset_vs()


def _make_store(mocker, *, exists=True, meta=None, docs=None, metas=None, raise_query=False):
    """Build a mock vector store with sensible defaults."""
    store = mocker.AsyncMock()
    store.collection_exists.return_value = exists
    store.get_collection_metadata.return_value = meta or {}
    if raise_query:
        store.query.side_effect = VectorStoreError("db error")
    else:
        store.query.return_value = QueryResult(
            ids=["id1", "id2"] if docs else [],
            documents=docs or [],
            metadatas=metas or [],
        )
    return store


def _make_embed_provider(mocker, provider_name="ollama", model_name="nomic-embed-text"):
    provider = mocker.MagicMock()
    provider.provider_name = provider_name
    provider.model_name = model_name
    return provider


class TestSearchContextNoDir:
    @pytest.mark.asyncio
    async def test_no_context_dir(self):
        result = await handle({"project_path": "/nonexistent", "query": "test"})
        assert "No .context/ directory found" in result[0].text


class TestSearchContextNotIndexed:
    @pytest.mark.asyncio
    async def test_collection_not_found(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, exists=False)
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)

        result = await handle({"project_path": str(project_dir), "query": "test"})
        assert "not found. Run index_project_context first." in result[0].text


class TestSearchContextSuccess:
    @pytest.mark.asyncio
    async def test_returns_formatted_results(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(
            mocker,
            docs=["Doc 1", "Doc 2"],
            metas=[{"file": "f1.md"}, {"file": "f2.md"}],
        )
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_context.embed_chunk",
            new_callable=mocker.AsyncMock,
            return_value=[0.1, 0.2],
        )
        mocker.patch(
            "mcp_project_context_server.tools.search_context.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        result = await handle({"project_path": str(project_dir), "query": "my query", "n_results": 2})

        text = result[0].text
        assert "[f1.md]" in text
        assert "Doc 1" in text
        assert "[f2.md]" in text
        assert "Doc 2" in text

    @pytest.mark.asyncio
    async def test_n_results_passed_to_store(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, docs=["Doc 1"], metas=[{"file": "f1.md"}])
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_context.embed_chunk",
            new_callable=mocker.AsyncMock,
            return_value=[0.1],
        )
        mocker.patch(
            "mcp_project_context_server.tools.search_context.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        await handle({"project_path": str(project_dir), "query": "q", "n_results": 7})

        store.query.assert_called_once()
        _, kwargs = store.query.call_args
        assert kwargs["n_results"] == 7

    @pytest.mark.asyncio
    async def test_no_results(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, docs=[], metas=[])
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_context.embed_chunk",
            new_callable=mocker.AsyncMock,
            return_value=[0.1],
        )
        mocker.patch(
            "mcp_project_context_server.tools.search_context.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        result = await handle({"project_path": str(project_dir), "query": "nothing"})
        assert "No results found." in result[0].text

    @pytest.mark.asyncio
    async def test_vector_store_error(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, raise_query=True)
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_context.embed_chunk",
            new_callable=mocker.AsyncMock,
            return_value=[0.1],
        )
        mocker.patch(
            "mcp_project_context_server.tools.search_context.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        assert "Search failed:" in result[0].text


class TestSearchContextMismatchWarning:
    @pytest.mark.asyncio
    async def test_no_warning_when_providers_match(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(
            mocker,
            meta={"embed_provider": "ollama", "embed_model": "nomic-embed-text"},
            docs=["Doc 1"],
            metas=[{"file": "f1.md"}],
        )
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_context.embed_chunk",
            new_callable=mocker.AsyncMock,
            return_value=[0.1],
        )
        mocker.patch(
            "mcp_project_context_server.tools.search_context.get_embedding_provider",
            return_value=_make_embed_provider(mocker, "ollama", "nomic-embed-text"),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        assert "mismatch" not in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_warning_when_provider_changed(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(
            mocker,
            meta={"embed_provider": "ollama", "embed_model": "nomic-embed-text"},
            docs=["Doc 1"],
            metas=[{"file": "f1.md"}],
        )
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_context.embed_chunk",
            new_callable=mocker.AsyncMock,
            return_value=[0.1],
        )
        mocker.patch(
            "mcp_project_context_server.tools.search_context.get_embedding_provider",
            return_value=_make_embed_provider(mocker, "voyage", "voyage-code-3"),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        text = result[0].text
        assert "mismatch" in text.lower()
        assert "ollama/nomic-embed-text" in text
        assert "voyage/voyage-code-3" in text

    @pytest.mark.asyncio
    async def test_warning_when_model_changed(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(
            mocker,
            meta={"embed_provider": "ollama", "embed_model": "nomic-embed-text"},
            docs=["Doc 1"],
            metas=[{"file": "f1.md"}],
        )
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_context.embed_chunk",
            new_callable=mocker.AsyncMock,
            return_value=[0.1],
        )
        mocker.patch(
            "mcp_project_context_server.tools.search_context.get_embedding_provider",
            return_value=_make_embed_provider(mocker, "ollama", "mxbai-embed-large"),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        text = result[0].text
        assert "mismatch" in text.lower()
        assert "nomic-embed-text" in text
        assert "mxbai-embed-large" in text

    @pytest.mark.asyncio
    async def test_no_warning_when_no_stored_metadata(self, tmp_path, mocker):
        """No stored provenance = index predates Phase 6; no warning emitted."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, meta={}, docs=["Doc 1"], metas=[{"file": "f1.md"}])
        mocker.patch("mcp_project_context_server.tools.search_context.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_context.embed_chunk",
            new_callable=mocker.AsyncMock,
            return_value=[0.1],
        )
        mocker.patch(
            "mcp_project_context_server.tools.search_context.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        assert "mismatch" not in result[0].text.lower()
