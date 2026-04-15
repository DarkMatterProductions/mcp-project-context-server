# ADR-00004: Modular tool handler architecture

## Status
Accepted

## Context

The initial implementation of the server was `context_server.py` — a monolithic file containing the MCP server loop, all four tool handler implementations, inline ChromaDB client initialization, and inline Ollama client calls. This approach had several practical problems:

- Adding a new tool required modifying `context_server.py` in multiple places: the tool definition list, the dispatch switch, and the handler implementation itself.
- External service clients (ChromaDB, Ollama) were initialized inline, making it impossible to test tool logic without running live external services.
- The tool handler logic, integration client setup, and indexing pipeline were mixed in the same file, making each harder to read in isolation.
- There was no clear boundary between "what the tool does" and "how it talks to external services."

The architecture needed a refactor that would let each concern grow independently, allow new tools to be added without touching existing code, and prepare the integration layer for future provider extensibility (see ADR-00003).

## Decision

The codebase was restructured into four layers, each with a single responsibility:

- **`tools/`**: One async handler module per MCP tool (`load_context.py`, `search_context.py`, `save_session.py`, `index_context.py`). Each exports a single `async handle(arguments: dict) -> list[types.TextContent]` function. Tool handlers never import from each other and never interact with external service clients directly.
- **`integrations/`**: External service client configuration and initialization (`chroma/client.py`, `ollama/client.py`). These modules own the singleton/factory pattern for each external service. They are the only place where ChromaDB or Ollama client setup appears.
- **`indexing/`**: The chunking, embedding, and vector store write pipeline (`chroma/indexer.py`, `ollama/embedder.py`). Orchestrates the full index rebuild: read files → chunk → embed → batch-add to ChromaDB. Imports from `integrations/` but not from `tools/`.
- **`helpers/`**: Shared utilities with no external service dependencies (`context.py`: `find_context_dir()`, `collection_name_for()`, `read_context_files()`). Importable by any layer.

`server.py` acts as the composition root: it imports tool handlers, registers tool definitions with MCP, and maintains a dispatch dict mapping tool names to handler functions. Adding a new tool requires only a new file in `tools/`, a new entry in the tool definitions list, and a new entry in the dispatch dict.

`context_server.py` is now legacy dead code. It is not referenced by any entry point and should be removed in a future cleanup.

## Consequences

- Adding a new tool is additive: create a new file, add two entries to `server.py`. No existing files need to be modified.
- Each layer is independently testable. Tool handlers can be tested by mocking the `integrations/` layer. The indexing pipeline can be tested against a test ChromaDB instance without invoking the MCP server.
- `context_server.py` remains in the repository as dead code. It duplicates all tool logic and will diverge over time if not removed.
- The dispatch dict in `server.py` is a simple `dict[str, Callable]`. It does not perform validation or provide plugin-style registration. This is intentional — the current tool count does not justify a plugin system.

## Alternatives Considered

- **Keep the monolith (`context_server.py`)**: Rejected. Does not scale as the tool count grows. Makes the integration layer impossible to swap (relevant for ADR-00003's planned cloud provider support).
- **Plugin registry / entry-point-based tool loading**: Rejected. Over-engineered for the current tool count (~4–15 tools). Dynamic loading adds indirection with no present benefit.
