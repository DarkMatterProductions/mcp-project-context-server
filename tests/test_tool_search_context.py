"""Tests for tools/search_context.py — updated to use vector store registry."""

import pytest
from pytest_mock import MockerFixture

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)
from mcp_project_context_server.tools.search_context import handle

_GET_VECTOR_STORE = "mcp_project_context_server.tools.search_context.get_vector_store"
_EMBED_CHUNK = "mcp_project_context_server.tools.search_context.embed_chunk"


@pytest.fixture()
def context_dir(tmp_path):
    """Create a tmp project dir with a .context/ subdirectory."""
    project = tmp_path / "project"
    project.mkdir()
    (project / ".context").mkdir()
    return project


@pytest.fixture()
def mock_store(mocker: MockerFixture):
    """Return a mock vector store injected via get_vector_store."""
    store = mocker.MagicMock()
    store.collection_exists = mocker.AsyncMock(return_value=True)
    store.query = mocker.AsyncMock(
        return_value=QueryResult(
            ids=["id1", "id2"],
            documents=["Doc 1", "Doc 2"],
            metadatas=[{"file": "f1.md"}, {"file": "f2.md"}],
        )
    )
    mocker.patch(_GET_VECTOR_STORE, return_value=store)
    return store


@pytest.fixture()
def mock_embed(mocker: MockerFixture):
    return mocker.patch(_EMBED_CHUNK, new_callable=mocker.AsyncMock, return_value=[0.1, 0.2])


# ---------------------------------------------------------------------------
# No .context/ directory
# ---------------------------------------------------------------------------


class TestNoContextDir:
    @pytest.mark.asyncio
    async def test_returns_no_context_dir_message(self) -> None:
        result = await handle({"project_path": "/nonexistent/path", "query": "test"})
        assert "No .context/ directory found" in result[0].text


# ---------------------------------------------------------------------------
# Collection not indexed
# ---------------------------------------------------------------------------


class TestCollectionNotIndexed:
    @pytest.mark.asyncio
    async def test_returns_not_indexed_message(
        self, context_dir, mocker: MockerFixture
    ) -> None:
        store = mocker.MagicMock()
        store.collection_exists = mocker.AsyncMock(return_value=False)
        mocker.patch(_GET_VECTOR_STORE, return_value=store)

        result = await handle({"project_path": str(context_dir), "query": "something"})
        assert "not found. Run index_project_context first." in result[0].text


# ---------------------------------------------------------------------------
# Successful search
# ---------------------------------------------------------------------------


class TestSuccessfulSearch:
    @pytest.mark.asyncio
    async def test_returns_formatted_markdown(
        self, context_dir, mock_store, mock_embed
    ) -> None:
        result = await handle({"project_path": str(context_dir), "query": "what is this?"})

        assert len(result) == 1
        text = result[0].text
        assert "**[f1.md]**" in text
        assert "Doc 1" in text
        assert "**[f2.md]**" in text
        assert "Doc 2" in text

    @pytest.mark.asyncio
    async def test_n_results_passed_through_to_store_query(
        self, context_dir, mock_store, mock_embed
    ) -> None:
        await handle({"project_path": str(context_dir), "query": "q", "n_results": 7})

        _, kwargs = mock_store.query.call_args
        assert kwargs["n_results"] == 7


# ---------------------------------------------------------------------------
# No results
# ---------------------------------------------------------------------------


class TestNoResults:
    @pytest.mark.asyncio
    async def test_returns_no_results_message(
        self, context_dir, mocker: MockerFixture
    ) -> None:
        store = mocker.MagicMock()
        store.collection_exists = mocker.AsyncMock(return_value=True)
        store.query = mocker.AsyncMock(
            return_value=QueryResult(ids=[], documents=[], metadatas=[])
        )
        mocker.patch(_GET_VECTOR_STORE, return_value=store)
        mocker.patch(_EMBED_CHUNK, new_callable=mocker.AsyncMock, return_value=[0.1])

        result = await handle({"project_path": str(context_dir), "query": "nothing"})
        assert "No results found." in result[0].text


# ---------------------------------------------------------------------------
# VectorStoreError
# ---------------------------------------------------------------------------


class TestVectorStoreErrorHandling:
    @pytest.mark.asyncio
    async def test_returns_search_failed_message_on_vector_store_error(
        self, context_dir, mocker: MockerFixture
    ) -> None:
        store = mocker.MagicMock()
        store.collection_exists = mocker.AsyncMock(return_value=True)
        store.query = mocker.AsyncMock(side_effect=VectorStoreError("connection lost"))
        mocker.patch(_GET_VECTOR_STORE, return_value=store)
        mocker.patch(_EMBED_CHUNK, new_callable=mocker.AsyncMock, return_value=[0.1])

        result = await handle({"project_path": str(context_dir), "query": "q"})
        assert "Search failed:" in result[0].text
        assert "connection lost" in result[0].text
