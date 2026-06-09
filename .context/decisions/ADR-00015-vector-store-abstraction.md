# ADR-00015: Vector Store Provider Abstraction

**Status:** Accepted
**Date:** 2026-06-08
**Author:** Hermes Agent

## Context

ChromaDB was hard-coded as the sole vector store. For team and enterprise
deployments, a shared or remote vector store is required: multiple server
instances or CI pipelines need to read and write the same index. ChromaDB's
local `PersistentClient` is not suitable for multi-tenant or
horizontally-scaled deployments because it is single-node and cannot be shared
across processes on different machines.

## Decision

Introduce a `VectorStoreProvider` Protocol with the following methods:
`create_collection`, `delete_collection`, `upsert`, `query`, `count`,
`collection_exists`, `get_collection_metadata`. Three implementations are
provided:

- `chroma-local` (`VECTOR_STORE_PROVIDER=chroma-local`) — local
  `PersistentClient`, default. Backward compatible with all existing
  deployments.
- `chroma-http` (`VECTOR_STORE_PROVIDER=chroma-http`) — remote `HttpClient`
  for shared deployments. Requires `CHROMA_HOST` and optionally `CHROMA_PORT`.
- `pgvector` (`VECTOR_STORE_PROVIDER=pgvector`) — PostgreSQL with the pgvector
  extension. Requires `DATABASE_URL`. Collection metadata is stored in a
  sidecar table for provenance tracking.

The default is `chroma-local` (backward compatible). The registry is driven by
`VECTOR_STORE_PROVIDER`.

## Rationale

- **`chroma-local` default**: preserves backward compatibility — no environment
  change required for existing local developer setups.
- **pgvector over Weaviate/Pinecone/Qdrant**: self-hostable with no additional
  infrastructure for teams already running PostgreSQL; SQL-native for metadata
  queries; strong ecosystem; no vendor lock-in.
- **Collection metadata in sidecar table** (pgvector) / **collection metadata**
  (ChromaDB): enables provenance tracking — records which embedding provider and
  model built each collection, enabling mismatch detection on startup.
- **Protocol design**: identical rationale as ADR-00014 — structural subtyping,
  no forced inheritance, easy addition of future stores.

## Consequences

- New vector stores can be added by implementing the Protocol and adding one
  registry entry — no changes to indexing or tool-handler code.
- `pgvector` requires `asyncpg` and the `pgvector` PostgreSQL extension
  (`CREATE EXTENSION vector`). These are not installed by default; they are
  available via `pip install ...[pgvector]`.
- The drop-and-recreate re-index strategy (ADR-00006) is preserved across all
  three implementations.
- `chroma-http` deployments must ensure the remote ChromaDB server is reachable
  and that auth tokens are configured if the server requires them.

## Alternatives Considered

- **Weaviate**: excellent feature set but requires separate infrastructure setup
  even for self-hosted deployments. Adds operational complexity for teams that
  don't already run Weaviate. Rejected for initial implementation.
- **Pinecone**: cloud-only, adds per-query cost, introduces vendor lock-in.
  Rejected.
- **Qdrant**: high-performance and self-hostable, but less SQL-native than
  pgvector for teams already on PostgreSQL who want unified infrastructure.
  Remains a viable future addition via the Protocol abstraction.
