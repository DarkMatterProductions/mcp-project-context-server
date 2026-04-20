# ADR-00002: ChromaDB as the vector store

## Status
Implemented

## Context

`mcp-project-context-server` requires persistent vector storage to support semantic search over indexed `.context/` files. The vector store must survive process restarts and be queryable on subsequent calls to `search_project_context`. The following options were evaluated:

- **ChromaDB**: Open-source vector database. Supports an embedded mode that runs fully in-process — no separate server or container needed. Persists to a local directory. Python-native API.
- **Qdrant**: High-performance vector database. Requires a running Docker container or Qdrant Cloud account. Not embeddable.
- **Weaviate**: Feature-rich vector database with GraphQL API. Also requires a running Docker container or managed cloud.
- **pgvector**: PostgreSQL extension for vector similarity search. Requires a running Postgres instance.
- **In-memory numpy arrays**: No external dependencies. Fast for small datasets. No persistence — the index is lost on process restart.

The server runs as a local subprocess on a developer's machine. The `.context/` directories it indexes are small (tens to low hundreds of markdown files). Infrastructure overhead should be minimized.

## Decision

ChromaDB with a persistent local client was chosen. The data directory defaults to `~/.mcp-data/chroma`, keeping indexed data outside the project tree and outside version control. The collection name for each project is derived from the project directory name using `collection_name_for()` in `helpers/context.py` — clamped to 63 characters with only safe characters (`[a-z0-9_-]`).

ChromaDB's embedded mode eliminates all deployment prerequisites: no Docker, no external server process, no credentials. The Python API is straightforward and supports the operations needed: create/drop collections, batch-add documents with embeddings and metadata, and query by vector similarity.

## Consequences

- ChromaDB is not designed for multi-process concurrent writes. This is acceptable: the server runs as a single process per project.
- Collection names are derived from the project directory name. If two different projects share a directory name, their collections will collide in the shared `~/.mcp-data/chroma` store. The current naming strategy does not include the full path, only the directory name.
- Indexed data is not committed to version control. A fresh checkout of the project requires running `index_project_context` before `search_project_context` will return results.
- ChromaDB's embedded mode is single-node only. If multi-user or distributed access is ever required, a migration to a server-mode ChromaDB instance or a different vector database would be needed.

## Alternatives Considered

- **Qdrant / Weaviate**: Rejected. Both require Docker or a managed cloud service — disproportionate infrastructure for a local developer tool.
- **pgvector**: Rejected. Requires a running PostgreSQL instance. Same infrastructure concern as above.
- **In-memory numpy arrays**: Rejected. No persistence. The index is rebuilt from scratch on every server start, which defeats the purpose of a persistent context server.
