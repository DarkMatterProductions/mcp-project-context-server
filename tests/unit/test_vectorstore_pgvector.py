"""Tests for PgVectorStoreProvider (integrations/vectorstore/pgvector/client.py).

asyncpg is mocked completely — no real PostgreSQL required.
"""

import json
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_async_cm(conn: MagicMock) -> MagicMock:
    """Return an async context manager mock that yields *conn* on each call."""

    class _AsyncCM:
        async def __aenter__(self) -> MagicMock:
            return conn

        async def __aexit__(self, *_: object) -> None:
            pass

    cm = MagicMock()
    cm.return_value = _AsyncCM()
    # Recreate the async-cm each time acquire() is called
    cm.side_effect = lambda: _AsyncCM()
    return cm


def _make_pool(conn: MagicMock) -> MagicMock:
    """Return a pool mock whose acquire() is an async context manager."""
    pool = MagicMock()
    pool.acquire = _make_async_cm(conn)
    pool.close = AsyncMock()
    return pool


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_asyncpg(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Insert a mock asyncpg module into sys.modules."""
    mock = MagicMock()
    monkeypatch.setitem(sys.modules, "asyncpg", mock)
    return mock


@pytest.fixture()
def provider(monkeypatch: pytest.MonkeyPatch, mock_asyncpg: MagicMock):
    monkeypatch.setenv("PGVECTOR_CONNECTION_STRING", "postgresql://user:***@localhost/db")
    from mcp_project_context_server.integrations.vectorstore.pgvector.client import PgVectorStoreProvider

    p = PgVectorStoreProvider()
    p.reset_for_testing()
    return p


@pytest.fixture()
def conn() -> AsyncMock:
    """A fresh async mock connection."""
    return AsyncMock()


@pytest.fixture()
def pool_provider(provider, conn: AsyncMock):
    """Provider with a pre-injected mock pool — no async setup required."""
    pool = _make_pool(conn)
    provider._pool = pool
    return provider, pool, conn


# ---------------------------------------------------------------------------
# __init__ guard
# ---------------------------------------------------------------------------


class TestInit:
    def test_raises_environment_error_when_connection_string_not_set(
        self, monkeypatch: pytest.MonkeyPatch, mock_asyncpg: MagicMock
    ) -> None:
        monkeypatch.delenv("PGVECTOR_CONNECTION_STRING", raising=False)
        from mcp_project_context_server.integrations.vectorstore.pgvector.client import PgVectorStoreProvider

        with pytest.raises(EnvironmentError, match="PGVECTOR_CONNECTION_STRING"):
            PgVectorStoreProvider()


# ---------------------------------------------------------------------------
# provider_name
# ---------------------------------------------------------------------------


class TestProviderName:
    def test_provider_name(self, provider) -> None:
        assert provider.provider_name == "pgvector"


# ---------------------------------------------------------------------------
# ImportError when asyncpg is absent
# ---------------------------------------------------------------------------


class TestImportError:
    @pytest.mark.asyncio
    async def test_raises_import_error_when_asyncpg_not_installed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PGVECTOR_CONNECTION_STRING", "postgresql://x:***@h/db")
        # Block asyncpg re-import so the lazy import inside _get_pool() fails
        monkeypatch.setitem(sys.modules, "asyncpg", None)

        from mcp_project_context_server.integrations.vectorstore.pgvector.client import PgVectorStoreProvider

        p = PgVectorStoreProvider()
        p.reset_for_testing()

        with pytest.raises(ImportError, match="asyncpg"):
            await p._get_pool()


# ---------------------------------------------------------------------------
# create_collection
# ---------------------------------------------------------------------------


class TestCreateCollection:
    @pytest.mark.asyncio
    async def test_create_collection_executes_expected_sql(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.reset_mock()

        await provider.create_collection("test-col", metadata={"env": "prod"})

        calls = [str(c.args[0]).strip() for c in conn.execute.await_args_list if c.args]
        assert any("DROP TABLE IF EXISTS" in c for c in calls)
        assert any("DELETE FROM vs_collections" in c for c in calls)
        assert any("INSERT INTO vs_collections" in c for c in calls)


# ---------------------------------------------------------------------------
# delete_collection
# ---------------------------------------------------------------------------


class TestDeleteCollection:
    @pytest.mark.asyncio
    async def test_delete_collection_executes_drop_and_delete(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.reset_mock()

        await provider.delete_collection("my-col")

        calls = [str(c.args[0]).strip() for c in conn.execute.await_args_list if c.args]
        assert any("DROP TABLE IF EXISTS" in c for c in calls)
        assert any("DELETE FROM vs_collections" in c for c in calls)

    @pytest.mark.asyncio
    async def test_delete_collection_silently_handles_exception(self, provider, mock_asyncpg: MagicMock) -> None:
        mock_asyncpg.create_pool = AsyncMock(side_effect=Exception("connection refused"))
        # Must not raise
        await provider.delete_collection("anything")


# ---------------------------------------------------------------------------
# upsert
# ---------------------------------------------------------------------------


class TestUpsert:
    @pytest.mark.asyncio
    async def test_upsert_calls_execute_for_each_document(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.reset_mock()

        await provider.upsert(
            collection_name="col",
            ids=["a", "b"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            documents=["doc A", "doc B"],
            metadatas=[{"f": "1"}, {"f": "2"}],
        )

        execute_calls = conn.execute.await_args_list
        sql_strings = [str(c.args[0]).strip() for c in execute_calls if c.args]
        insert_calls = [s for s in sql_strings if "INSERT INTO" in s and "vs_collections" not in s]
        assert len(insert_calls) == 2  # one per document


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------


class TestQuery:
    @pytest.mark.asyncio
    async def test_query_returns_query_result_with_correct_fields(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider

        rows = [
            {"id": "id1", "document": "Doc 1", "metadata": json.dumps({"file": "f1.md"}), "similarity": 0.9},
            {"id": "id2", "document": "Doc 2", "metadata": json.dumps({"file": "f2.md"}), "similarity": 0.8},
        ]
        conn.fetch = AsyncMock(return_value=rows)

        result = await provider.query("col", [0.1, 0.2], n_results=2)

        assert result.ids == ["id1", "id2"]
        assert result.documents == ["Doc 1", "Doc 2"]
        assert result.metadatas == [{"file": "f1.md"}, {"file": "f2.md"}]
        assert result.distances == [0.9, 0.8]

    @pytest.mark.asyncio
    async def test_query_raises_vector_store_error_on_sql_failure(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.fetch = AsyncMock(side_effect=Exception("SQL error"))

        from mcp_project_context_server.integrations.vectorstore.base import VectorStoreError

        with pytest.raises(VectorStoreError, match="Query failed"):
            await provider.query("col", [0.1])


# ---------------------------------------------------------------------------
# count
# ---------------------------------------------------------------------------


class TestCount:
    @pytest.mark.asyncio
    async def test_count_returns_integer(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.fetchrow = AsyncMock(return_value={"n": 5})

        result = await provider.count("col")
        assert result == 5

    @pytest.mark.asyncio
    async def test_count_returns_zero_on_exception(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.fetchrow = AsyncMock(side_effect=Exception("table missing"))

        result = await provider.count("col")
        assert result == 0


# ---------------------------------------------------------------------------
# collection_exists
# ---------------------------------------------------------------------------


class TestCollectionExists:
    @pytest.mark.asyncio
    async def test_returns_true_when_sidecar_row_found(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.fetchrow = AsyncMock(return_value={"1": 1})

        assert await provider.collection_exists("col") is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_row(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.fetchrow = AsyncMock(return_value=None)

        assert await provider.collection_exists("col") is False


# ---------------------------------------------------------------------------
# get_collection_metadata
# ---------------------------------------------------------------------------


class TestGetCollectionMetadata:
    @pytest.mark.asyncio
    async def test_returns_parsed_json_dict(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.fetchrow = AsyncMock(return_value={"metadata": json.dumps({"env": "staging"})})

        result = await provider.get_collection_metadata("col")
        assert result == {"env": "staging"}

    @pytest.mark.asyncio
    async def test_returns_empty_dict_on_exception(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        conn.fetchrow = AsyncMock(side_effect=Exception("gone"))

        result = await provider.get_collection_metadata("col")
        assert result == {}


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------


class TestClose:
    @pytest.mark.asyncio
    async def test_close_closes_pool_and_sets_to_none(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        mock_pool = MagicMock()
        mock_pool.close = AsyncMock()
        provider._pool = mock_pool

        await provider.close()

        mock_pool.close.assert_awaited_once()
        assert provider._pool is None


# ---------------------------------------------------------------------------
# reset_for_testing
# ---------------------------------------------------------------------------


class TestResetForTesting:
    def test_reset_for_testing_sets_pool_to_none(self, pool_provider: tuple) -> None:
        provider, pool, conn = pool_provider
        assert provider._pool is not None
        provider.reset_for_testing()
        assert provider._pool is None
