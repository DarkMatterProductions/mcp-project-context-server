# ADR-00005: Environment variable configuration

## Status
Implemented

## Context

The server requires runtime configuration for five parameters:

- The Ollama server address (`OLLAMA_HOST`)
- The embedding model name (`EMBED_MODEL`)
- The ChromaDB persistence directory (`CHROMA_DIR`)
- The target project path (`PROJECT_PATH`)
- The embedding concurrency limit (`EMBED_CONCURRENCY`)

These values vary between users, machines, and projects. They should not be hardcoded. The following configuration mechanisms were considered:

- **Environment variables**: The standard mechanism for MCP client-server configuration. MCP clients (Claude Code, Continue IDE, etc.) have native support for passing environment variables to server subprocess invocations in their config blocks. No config file parsing required.
- **`.env` files**: Common for local development. Not loaded automatically by MCP client subprocess invocations — would require the server to call `python-dotenv` or equivalent at startup.
- **YAML config file**: Human-readable, supports comments, allows per-project configuration alongside the `.context/` directory. Requires `pyyaml` (already in `requirements.txt`). Needs a defined file location and a precedence rule relative to env vars.
- **Hardcoded defaults only**: Simple but inflexible. Would require code changes for every deployment variation.

MCP client config blocks pass environment variables to the spawned server subprocess. This is the path of least resistance for the primary deployment model.

## Decision

All runtime configuration is provided via environment variables. Defaults are set in the relevant module if no env var is present:

| Variable | Default | Module |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | `integrations/embeddings/ollama/client.py` |
| `EMBED_MODEL` | `nomic-embed-text` | `integrations/embeddings/ollama/client.py` |
| `EMBED_PROVIDER` | *(required — no default; fails fast if unset, per ADR-00024)* | `integrations/embeddings/registry.py` |
| `CHROMA_DIR` | `~/.mcp-data/chroma` | `integrations/vectorstore/chroma_local/client.py` |
| `CHROMA_HOST` | `localhost` | `integrations/vectorstore/chroma_http/client.py` |
| `CHROMA_PORT` | `8000` | `integrations/vectorstore/chroma_http/client.py` |
| `CHROMA_API_KEY` | *(unset)* | `integrations/vectorstore/chroma_http/client.py` |
| `PGVECTOR_CONNECTION_STRING` | *(required)* | `integrations/vectorstore/pgvector/client.py` |
| `VECTOR_STORE_PROVIDER` | `chroma-local` | `integrations/vectorstore/registry.py` |
| `PROJECT_PATH` | resolved at tool call time | `tools/*.py` |
| `EMBED_CONCURRENCY` | `4` | `indexing/indexer.py` |

> **Deprecated paths** (raise `RuntimeError` at call time):
> - `integrations/chroma/client.py` → use `integrations/vectorstore/chroma_local/client.py` or `chroma_http/client.py`
> - `indexing/chroma/indexer.py` → use `integrations/vectorstore/registry.get_indexer()` or the provider-owned indexer
> - `indexing/ollama/embedder.py` → use `indexing/embedder.py`

`pyyaml` is already present in `requirements.txt` in anticipation of a YAML configuration layer, which remains unimplemented — see ADR-00028.

## Consequences

- Users must configure environment variables in their MCP client settings block (e.g., the `env` section of a `mcp-servers.json` or equivalent). There is no config file to edit today.
- There is no central config module — each module reads its own env vars. This is consistent and avoids a global config object, but means there is no single place to audit all configuration.
- `pyyaml` is listed in `requirements.txt` but not in `pyproject.toml`. When the YAML layer is implemented, it must be added to `pyproject.toml` dependencies as well.
- `PROJECT_PATH` is handled differently from the others — it is read at tool call time in individual `tools/` handlers, not at server startup. This allows the same server process to serve multiple project paths if needed in future.
- Several individual variables and their implementation modules have since moved: `EMBED_PROVIDER` now resolves via a provider registry (ADR-00014) rather than a single hardcoded default, `CHROMA_*`/`PGVECTOR_*`/`VECTOR_STORE_PROVIDER` route through a vector store abstraction (ADR-00015), and provider configuration is now explicit with no shape inference (ADR-00024). The table above reflects that post-abstraction layout — the original `integrations/chroma/client.py` and `indexing/chroma/indexer.py` paths listed in earlier revisions of this table are deprecated. The env-var-based configuration mechanism itself (this decision) was not superseded by any of these — only the modules backing individual variables changed.

## Alternatives Considered

- **`.env` files**: Rejected as the primary mechanism. MCP client subprocesses do not automatically load `.env` files. Would require the server to add a `python-dotenv` dependency and startup-time file loading.
- **TOML config (pyproject.toml tool section)**: Rejected. `pyproject.toml` is a project metadata file, not a runtime config file. Mixing runtime config with build config creates ambiguity.
