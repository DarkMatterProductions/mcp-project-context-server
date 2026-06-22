"""ChromaDB HTTP (remote) vector store provider.

Configuration
-------------
``CHROMA_HOST``
    Hostname or IP of the ChromaDB server.  Defaults to ``localhost``.

``CHROMA_PORT``
    Port the server listens on.  Defaults to ``8000``.

``CHROMA_API_KEY``
    Optional static API key for ChromaDB's built-in auth.
    Leave unset if the server does not require authentication.
"""

import asyncio
import os
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)


class ChromaHttpVectorStoreProvider:
    """Vector store backed by a remote ChromaDB HTTP server.

    The chromadb ``HttpClient`` is initialized lazily on first use.
    """

    def __init__(self) -> None:
        self._host: str = os.getenv("CHROMA_HOST", "localhost")
        self._port: int = int(os.getenv("CHROMA_PORT", "8000"))
        self._api_key: Optional[str] = os.getenv("CHROMA_API_KEY") or None
        self._client: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        return "chroma-http"

    def _get_client(self) -> Any:
        """Return the ChromaDB HTTP client, initialising on first call."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            settings = Settings(anonymized_telemetry=False)
            if self._api_key:
                settings = Settings(
                    anonymized_telemetry=False,
                    chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                    chroma_client_auth_credentials=self._api_key,
                )
            self._client = chromadb.HttpClient(
                host=self._host,
                port=self._port,
                settings=settings,
            )
        return self._client

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Drop and recreate *name* (ADR-00006)."""
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass
            client.create_collection(name=name, metadata=metadata or {})

        await asyncio.to_thread(_sync)

    async def delete_collection(self, name: str) -> None:
        """Delete *name*, silently succeeding if absent."""
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass

        await asyncio.to_thread(_sync)

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Add or update documents."""
        client = self._get_client()

        def _sync() -> None:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            col.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

        await asyncio.to_thread(_sync)

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a nearest-neighbour search."""
        client = self._get_client()

        def _sync() -> QueryResult:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            n = min(n_results, col.count())
            if n == 0:
                return QueryResult(ids=[], documents=[], metadatas=[], distances=[])
            raw = col.query(query_embeddings=[query_embedding], n_results=n)
            return QueryResult(
                ids=raw["ids"][0] if raw.get("ids") else [],
                documents=raw["documents"][0] if raw.get("documents") else [],
                metadatas=raw["metadatas"][0] if raw.get("metadatas") else [],
                distances=raw["distances"][0] if raw.get("distances") else [],
            )

        return await asyncio.to_thread(_sync)

    async def count(self, collection_name: str) -> int:
        """Return document count (0 if collection absent)."""
        client = self._get_client()

        def _sync() -> int:
            try:
                return client.get_collection(collection_name).count()
            except Exception:
                return 0

        return await asyncio.to_thread(_sync)

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if *collection_name* exists."""
        client = self._get_client()

        def _sync() -> bool:
            try:
                client.get_collection(collection_name)
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_sync)

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return collection metadata (``{}`` if absent)."""
        client = self._get_client()

        def _sync() -> dict:
            try:
                col = client.get_collection(collection_name)
                return col.metadata or {}
            except Exception:
                return {}

        return await asyncio.to_thread(_sync)

    def reset_for_testing(self) -> None:
        """Reset the cached client.  **For use in tests only.**"""
        self._client = None
