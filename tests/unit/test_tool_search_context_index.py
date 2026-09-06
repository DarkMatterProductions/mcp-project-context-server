"""Tests for the search_context_index tool (whole-index semantic search)."""

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing as reset_repo
from mcp_project_context_server.integrations.vectorstore.base import QueryResult, VectorStoreError
from mcp_project_context_server.tools.search_context_index import handle


@pytest.fixture(autouse=True)
def reset_registries():
    reset_repo()
    yield
    reset_repo()


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
    provider.embed_chunk = mocker.AsyncMock(return_value=[0.1, 0.2])
    return provider


class TestSearchContextIndexNoDir:
    @pytest.mark.asyncio
    async def test_no_context_dir(self):
        result = await handle({"project_path": "/nonexistent", "query": "test"})
        assert "No .context/ directory found" in result.content[0].text
        assert result.structured_content == {"results": []}

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch, mocker):
        mock_store = mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store")
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo", "query": "test"})

        assert "not permitted" in result.content[0].text
        assert result.structured_content == {"results": []}
        mock_store.assert_not_called()


def _make_repo_provider(mocker, provider_name="github"):
    provider = mocker.MagicMock()
    provider.provider_name = provider_name
    return provider


class TestSearchContextIndexRemote:
    @pytest.mark.asyncio
    async def test_uses_repo_id_derived_collection_name(self, mocker):
        store = _make_store(mocker, exists=False)
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_repository_provider",
            return_value=_make_repo_provider(mocker),
        )

        result = await handle({"project_path": "owner/repo", "query": "test"})

        assert "not found. Run index_project_context first." in result.content[0].text
        assert result.structured_content == {"results": []}
        store.collection_exists.assert_called_once_with("ctx_owner_repo")

    @pytest.mark.asyncio
    async def test_url_form_resolves_to_same_collection(self, mocker):
        store = _make_store(mocker, exists=False)
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_repository_provider",
            return_value=_make_repo_provider(mocker),
        )

        await handle({"project_path": "https://github.com/owner/repo", "query": "test"})

        store.collection_exists.assert_called_once_with("ctx_owner_repo")

    @pytest.mark.asyncio
    async def test_short_identifier_shape_is_local_when_provider_is_local(self, tmp_path, monkeypatch, mocker):
        """Regression test for ADR-00024: an ``owner/repo``-shaped path must not be
        treated as remote when REPO_PROVIDER is local (the default)."""
        monkeypatch.chdir(tmp_path)
        store = _make_store(mocker, exists=False)
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)

        result = await handle({"project_path": "owner/repo", "query": "test"})

        assert "No .context/ directory found" in result.content[0].text
        assert result.structured_content == {"results": []}
        store.collection_exists.assert_not_called()


class TestSearchContextIndexNotIndexed:
    @pytest.mark.asyncio
    async def test_collection_not_found(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, exists=False)
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)

        result = await handle({"project_path": str(project_dir), "query": "test"})
        assert "not found. Run index_project_context first." in result.content[0].text
        assert result.structured_content == {"results": []}


class TestSearchContextIndexSuccess:
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
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        result = await handle({"project_path": str(project_dir), "query": "my query", "n_results": 2})

        text = result.content[0].text
        assert "[f1.md]" in text
        assert "Doc 1" in text
        assert "[f2.md]" in text
        assert "Doc 2" in text
        assert result.structured_content == {
            "results": [
                {"file": "f1.md", "chunk": None, "content": "Doc 1", "distance": None},
                {"file": "f2.md", "chunk": None, "content": "Doc 2", "distance": None},
            ]
        }

    @pytest.mark.asyncio
    async def test_n_results_passed_to_store(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, docs=["Doc 1"], metas=[{"file": "f1.md"}])
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
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
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        result = await handle({"project_path": str(project_dir), "query": "nothing"})
        assert "No results found." in result.content[0].text
        assert result.structured_content == {"results": []}

    @pytest.mark.asyncio
    async def test_vector_store_error(self, tmp_path, mocker):
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, raise_query=True)
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        assert "Search failed:" in result.content[0].text
        assert result.structured_content == {"results": []}


class TestSearchContextIndexMismatchWarning:
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
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
            return_value=_make_embed_provider(mocker, "ollama", "nomic-embed-text"),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        assert "mismatch" not in result.content[0].text.lower()
        assert "warning" not in result.structured_content

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
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
            return_value=_make_embed_provider(mocker, "voyage", "voyage-code-3"),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        text = result.content[0].text
        assert "mismatch" in text.lower()
        assert "ollama/nomic-embed-text" in text
        assert "voyage/voyage-code-3" in text
        assert "mismatch" in result.structured_content["warning"].lower()

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
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
            return_value=_make_embed_provider(mocker, "ollama", "mxbai-embed-large"),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        text = result.content[0].text
        assert "mismatch" in text.lower()
        assert "nomic-embed-text" in text
        assert "mxbai-embed-large" in text
        assert "mismatch" in result.structured_content["warning"].lower()

    @pytest.mark.asyncio
    async def test_no_warning_when_no_stored_metadata(self, tmp_path, mocker):
        """No stored provenance = index predates Phase 6; no warning emitted."""
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        store = _make_store(mocker, meta={}, docs=["Doc 1"], metas=[{"file": "f1.md"}])
        mocker.patch("mcp_project_context_server.tools.search_shared.get_vector_store", return_value=store)
        mocker.patch(
            "mcp_project_context_server.tools.search_shared.get_embedding_provider",
            return_value=_make_embed_provider(mocker),
        )

        result = await handle({"project_path": str(project_dir), "query": "q"})
        assert "mismatch" not in result.content[0].text.lower()
        assert "warning" not in result.structured_content
