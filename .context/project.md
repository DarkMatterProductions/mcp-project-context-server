# Project: mcp-project-context-server

## One-liner

A Python MCP server that gives LLMs persistent, searchable access to project context — documentation, architecture decisions, and session notes — stored in a structured `.context/` directory alongside any codebase.

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: MCP (Model Context Protocol), stdio transport
- **Key Libraries**: `chromadb` (vector store), `ollama` (embeddings), `watchdog` (planned: auto-reindex), `pyyaml` (planned: YAML config), `mcp` (server framework)
- **Database**: ChromaDB — embedded, persistent, local at `~/.mcp-data/chroma`
- **Build System**: Hatchling (PEP 517)

## Architecture

The server uses a 4-layer modular structure. Each layer has a single responsibility and depends only on the layer below it.

```
src/mcp_project_context_server/
├── server.py              # MCP server entry point; tool registration and dispatch
├── tools/                 # One async handler module per MCP tool
│   ├── load_context.py    # load_project_context
│   ├── search_context.py  # search_project_context
│   ├── save_session.py    # save_session_summary
│   └── index_context.py   # index_project_context
├── integrations/          # External service clients (provider-agnostic interface boundary)
│   ├── chroma/client.py   # ChromaDB singleton — persistent local client
│   └── ollama/client.py   # Ollama sync + async clients; embed() wrappers
├── indexing/              # Chunking, embedding, and vector store write pipeline
│   ├── chroma/indexer.py  # Async pipeline: read → chunk → embed → batch-add to ChromaDB
│   └── ollama/embedder.py # Thin wrappers around integrations/ollama/client
└── helpers/
    └── context.py         # find_context_dir(), collection_name_for(), read_context_files()
```

**Data flow for `index_project_context`:**
1. `find_context_dir()` walks up from `PROJECT_PATH` to locate `.context/`
2. `read_context_files()` reads all `.md` files recursively
3. Files are chunked (currently fixed 1000-char; heading-boundary under review — see ADR-00007)
4. Chunks are embedded concurrently via Ollama (bounded by `EMBED_CONCURRENCY` semaphore)
5. All valid embeddings are batch-added to a ChromaDB collection named after the project directory

**Data flow for `search_project_context`:**
1. Query is embedded via Ollama
2. ChromaDB performs cosine-similarity search against the project collection
3. Top-N results returned with source filename metadata

## Key Conventions

- **Async throughout**: All tool handlers and indexing logic use `async`/`await`. Both sync and async Ollama clients are provided for flexibility.
- **POSIX paths for IDs**: ChromaDB document IDs and metadata keys always use `.as_posix()` — never `str(Path(...))` — ensuring cross-platform consistency (see ADR-00008).
- **Env var configuration**: All runtime config is via environment variables. No hardcoded paths. See entry in *Entry Points* for the full variable list.
- **Tool handlers never throw**: All `tools/` handlers catch errors and return `types.TextContent` with an informative message. MCP clients receive a human-readable error, not a crash.
- **Collection naming**: `collection_name_for(context_dir)` derives a stable, safe ChromaDB collection name from the project directory name. Names are clamped to 63 characters with only `[a-z0-9_-]` characters.
- **`find_context_dir()` contract**: Walks up from the given path until `.context/` is found or the filesystem root is reached. Returns `None` if not found — callers handle this gracefully.

## ADRs

Architecture Decision Records live in `.context/decisions/`. They capture not just what was decided, but why — including alternatives considered and consequences.

- **ADR-00001 through ADR-00008**: Accepted — document the current architecture
- **ADR-00007**: Under Review — chunking strategy (heading-boundary vs fixed-size)
- **ADR-00009 through ADR-00011**: Proposed — planned tool groups

Reference ADRs before making significant design choices. ADRs are indexed and searchable via the `search_project_context` MCP tool — query them by topic (e.g., `"embedding provider"`, `"chunking"`, `"repomix"`).

Naming convention: `ADR-XXXXX-{kebab-case-topic}.md` (5-digit zero-padded, sequential, never reused).

## Current Active Work

Three tool groups are planned and in early design (see ADRs 00009–00011):

1. **Repomix integration** (`ADR-00009`): Tools to trigger repomix processing on the current project, consume the generated markdown snapshot, and feed it into the indexing pipeline — enabling semantic search over source code in addition to documentation.

2. **ADR tooling** (`ADR-00010`): First-class MCP tools for the ADR lifecycle — list ADRs with status, read individual ADR content, update status/body, and scaffold new ADRs from the standard template with auto-assigned sequential numbers.

3. **Repository bootstrapping** (`ADR-00011`): A `bootstrap_context` tool that generates a complete `.context/` skeleton (project.md stub, decisions/, sessions/) for any new project by inspecting `pyproject.toml`, `package.json`, or `README.md`.

## Known Pain Points / Tech Debt

- **`watchdog` dependency**: Present in `requirements.txt` for planned auto-reindex feature (ADR-00006). Not yet implemented in code.
- **`pyyaml` dependency**: Present in `requirements.txt` for planned YAML configuration layer (ADR-00005). Not yet implemented in code. Also absent from `pyproject.toml` — needs to be added when the feature lands.
- **Chunk size not configurable**: The 1000-character chunk size in `indexing/chroma/indexer.py` is a hardcoded constant. Not exposed as an env var. Currently Under Review (ADR-00007).
- **No tests**: The only test artifact is `scripts/test_client.py`, which is a manual integration smoke-test. No unit or integration test suite exists.

## Entry Points

- **CLI**: `project-context-server` — installed by pip via `[project.scripts]` in `pyproject.toml`; invokes `mcp_project_context_server.server:run`
- **Module**: `python -m mcp_project_context_server` — calls `server.run()` via `__main__.py`
- **MCP tools exposed**:
  - `load_project_context` — reads and concatenates `project.md`, all ADRs, and the most recent session file
  - `search_project_context(query, n_results=5)` — semantic search over the indexed `.context/` collection
  - `save_session_summary(summary)` — appends a dated session note to `.context/sessions/YYYY-MM-DD.md`
  - `index_project_context` — rebuilds the ChromaDB collection from `.context/` (drop and recreate)
- **Environment variables**:
  - `PROJECT_PATH` — path to the project root (optional; defaults to CWD resolution)
  - `OLLAMA_HOST` — Ollama server URL (default: `http://localhost:11434`)
  - `EMBED_MODEL` — embedding model name (default: `nomic-embed-text`)
  - `CHROMA_DIR` — ChromaDB persistence directory (default: `~/.mcp-data/chroma`)
  - `EMBED_CONCURRENCY` — max concurrent embedding requests (default: `4`)
