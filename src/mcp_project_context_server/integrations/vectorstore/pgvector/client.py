"""PostgreSQL + pgvector vector store provider.

Configuration
-------------
``PGVECTOR_CONNECTION_STRING``
    A libpq-compatible connection string, e.g.:
    ``postgresql://{user}:{password}@{host}:5432/dbname``

Design
------
* One table per collection: ``vs_<sanitised_collection_name>``
* A ``vs_collections`` sidecar table stores collection metadata and the
  embedding dimension (derived from the first upsert call).
* Vectors are stored as ``vector(N)`` using the pgvector extension.
* The drop-and-recreate indexing strategy (ADR-00006) is implemented by
  ``create_collection`` — it drops the table and recreates it.
"""
import logging
import os
import re
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)

logger = logging.getLogger(__name__)

_TABLE_PREFIX = "vs_"


def _table_name(collection_name: str) -> str:
    """Sanitise *collection_name* into a safe PostgreSQL table name."""
    safe = re.sub(r"[^a-z0-9_]", "_", collection_name.lower())
    return f"{_TABLE_PREFIX}{safe}"


class PgVectorStoreProvider:
    """Vector store backed by PostgreSQL with the pgvector extension.

    Uses ``asyncpg`` for async PostgreSQL access.  The pgvector extension
    must already be installed in the target database::

        CREATE EXTENSION IF NOT EXISTS vector;
    """

    def __init__(self) -> None:
        """Initialize the provider, reading ``PGVECTOR_CONNECTION_STRING`` from the environment.

        :raises EnvironmentError: If ``PGVECTOR_CONNECTION_STRING`` is not set.
        """
        self._dsn: Optional[str] = os.getenv("PGVECTOR_CONNECTION_STRING")
        if not self._dsn:
            raise EnvironmentError(
                "PGVECTOR_CONNECTION_STRING environment variable is required " "when VECTOR_STORE_PROVIDER=pgvector"
            )
        self._pool: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "pgvector"

    async def _get_pool(self) -> Any:
        """Return the asyncpg connection pool, creating it on first call."""
        if self._pool is None:
            try:
                import asyncpg  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "asyncpg is required for pgvector support.  "
                    "Install it with: pip install mcp-project-context-server[pgvector]"
                ) from exc

            # Register the pgvector codec so asyncpg can decode vector columns
            async def _init(conn: Any) -> None:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")  # type: ignore[attr-defined]
                await conn.set_type_codec(  # type: ignore[attr-defined]
                    "vector",
                    encoder=lambda v: str(v),
                    decoder=lambda v: [float(x) for x in v.strip("[]").split(",")],
                    schema="public",
                    format="text",
                )

            self._pool = await asyncpg.create_pool(self._dsn, init=_init)  # type: ignore[attr-defined]

            # Ensure sidecar table exists
            async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS vs_collections (
                        name        TEXT PRIMARY KEY,
                        dimension   INT,
                        metadata    JSONB DEFAULT '{}'
                    )
                """)

        return self._pool

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Drop and recreate the table for *name* (ADR-00006).

        Dimension is not known at creation time — the vector column is added
        on the first ``upsert`` call once the dimension is established.

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        pool = await self._get_pool()
        tbl = _table_name(name)
        import json

        async with pool.acquire() as conn:  # type: ignore[attr-defined]
            await conn.execute(f"DROP TABLE IF EXISTS {tbl}")
            await conn.execute("DELETE FROM vs_collections WHERE name = $1", name)
            await conn.execute(
                "INSERT INTO vs_collections (name, dimension, metadata) VALUES ($1, NULL, $2::jsonb)",
                name,
                json.dumps(metadata or {}),
            )

    async def delete_collection(self, name: str) -> None:
        """Drop the table for *name* and remove from sidecar.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        try:
            pool = await self._get_pool()
            tbl = _table_name(name)
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                await conn.execute(f"DROP TABLE IF EXISTS {tbl}")
                await conn.execute("DELETE FROM vs_collections WHERE name = $1", name)
        except Exception:
            pass

    async def _ensure_table(self, conn: Any, name: str, dimension: int) -> None:
        """Create the vector table for *name* if it does not yet exist."""
        tbl = _table_name(name)
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {tbl} (
                id          TEXT PRIMARY KEY,
                embedding   vector({dimension}),
                document    TEXT,
                metadata    JSONB DEFAULT '{{}}'
            )
            """)  # type: ignore[attr-defined]
        await conn.execute(  # type: ignore[attr-defined]
            f"CREATE INDEX IF NOT EXISTS {tbl}_emb_idx ON {tbl} USING ivfflat (embedding vector_cosine_ops)"
        )
        await conn.execute(  # type: ignore[attr-defined]
            "UPDATE vs_collections SET dimension = $1 WHERE name = $2 AND dimension IS NULL",
            dimension,
            name,
        )

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Insert or update documents in *collection_name*.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        """
        if not ids:
            return
        import json

        dimension = len(embeddings[0])
        pool = await self._get_pool()
        tbl = _table_name(collection_name)

        async with pool.acquire() as conn:  # type: ignore[attr-defined]
            await self._ensure_table(conn, collection_name, dimension)
            for doc_id, emb, doc, meta in zip(ids, embeddings, documents, metadatas):
                vec_str = "[" + ",".join(str(v) for v in emb) + "]"
                await conn.execute(  # type: ignore[attr-defined]
                    f"""
                    INSERT INTO {tbl} (id, embedding, document, metadata)
                    VALUES ($1, $2::vector, $3, $4::jsonb)
                    ON CONFLICT (id) DO UPDATE
                        SET embedding = EXCLUDED.embedding,
                            document  = EXCLUDED.document,
                            metadata  = EXCLUDED.metadata
                    """,
                    doc_id,
                    vec_str,
                    doc,
                    json.dumps(meta),
                )

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run cosine-similarity nearest-neighbour search.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the query fails.
        """
        import json

        pool = await self._get_pool()
        tbl = _table_name(collection_name)
        vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        try:
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                rows = await conn.fetch(  # type: ignore[attr-defined]
                    f"""
                    SELECT id, document, metadata,
                           1 - (embedding <=> $1::vector) AS similarity
                    FROM {tbl}
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2
                    """,
                    vec_str,
                    n_results,
                )
        except Exception as exc:
            raise VectorStoreError(f"Query failed on collection '{collection_name}': {exc}") from exc

        return QueryResult(
            ids=[r["id"] for r in rows],
            documents=[r["document"] for r in rows],
            metadatas=[json.loads(r["metadata"]) for r in rows],
            distances=[float(r["similarity"]) for r in rows],
        )

    async def count(self, collection_name: str) -> int:
        """Return document count (0 if table absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        try:
            pool = await self._get_pool()
            tbl = _table_name(collection_name)
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(f"SELECT COUNT(*) AS n FROM {tbl}")  # type: ignore[attr-defined]
                return int(row["n"])
        except Exception:
            return 0

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if a row exists in the sidecar for *collection_name*.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(  # type: ignore[attr-defined]
                    "SELECT 1 FROM vs_collections WHERE name = $1", collection_name
                )
                return row is not None
        except Exception:
            return False

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return metadata from the sidecar (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """
        try:
            import json

            pool = await self._get_pool()
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(  # type: ignore[attr-defined]
                    "SELECT metadata FROM vs_collections WHERE name = $1", collection_name
                )
                if row is None:
                    return {}
                return json.loads(row["metadata"]) if row["metadata"] else {}
        except Exception:
            return {}

    async def close(self) -> None:
        """Close the connection pool.  Call on server shutdown.

        :return: (None) This method does not return a value.
        """
        if self._pool is not None:
            await self._pool.close()  # type: ignore[attr-defined]
            self._pool = None

    def reset_for_testing(self) -> None:
        """Reset the cached pool.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._pool = None
