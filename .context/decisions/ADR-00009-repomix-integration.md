# ADR-00009: Repomix integration

## Status
Proposed

## Context

Repomix is a tool that generates a single flat markdown file containing the full contents of a codebase — every source file concatenated with metadata headers. Indexing this snapshot into the context server's vector store would extend semantic search beyond `.context/` documentation files to cover the actual source code of the project.

This is particularly valuable for an agent working on `mcp-project-context-server` itself: it would be able to search not just the ADRs and project overview, but the actual tool handler implementations, integration clients, and helper utilities.

Two sub-decisions are required:

**Sub-decision 1 — Invocation:** How should the server trigger repomix?
- **Subprocess invocation**: Shell out to `repomix` CLI. Requires repomix to be installed on the host machine (`npm install -g repomix`). Simple implementation, no protocol overhead.
- **MCP client call to a repomix MCP server**: Repomix provides its own MCP server. The context server could act as an MCP client and call the repomix MCP server's tools. Requires the repomix MCP server to be configured in the user's MCP environment. More complex, but avoids a direct CLI dependency.
- **Pre-generated output only**: Do not trigger repomix at all. Expect the user to generate the repomix output file manually and place it at a known location (e.g., `.context/repomix-output.md`). The context server then indexes it as a regular `.md` file. Simplest implementation — no invocation logic needed.

**Sub-decision 2 — Storage:** Where does the repomix output live and how is it indexed?
- **Alongside `.context/` markdown files** (`project.md`, ADRs): The repomix output is indexed into the same ChromaDB collection as documentation. A single `search_project_context` query returns results from both documentation and code.
- **Separate ChromaDB collection** (e.g., `{project}-code`): Code is indexed separately from documentation. Allows callers to target searches at code vs. documentation specifically. Requires a new `search_code_context` tool or a `collection` parameter on the existing search tool.

**Chunk size consideration:** Repomix output files can be very large (megabytes for large codebases). The current fixed 1000-character chunking strategy (ADR-00007) would produce thousands of chunks. The heading-boundary approach under review in ADR-00007 may be better suited for repomix output, since repomix uses markdown headings to delimit individual files.

## ADR Review Discussion

1. **Pre-generated output as the first milestone**: The simplest path to value is to support pre-generated repomix output as a regular `.context/` file. No invocation logic, no MCP client complexity — just drop `repomix-output.md` in `.context/` and it gets indexed automatically. This can ship immediately. Subprocess or MCP invocation can be added as a follow-on.

2. **Subprocess invocation as the preferred trigger**: If the server is to trigger repomix, subprocess invocation is simpler than acting as an MCP client. The tradeoff is a `repomix` CLI dependency. This is acceptable for power users; it should not be required for the base installation.

3. **Separate collection vs. merged**: A separate `{project}-code` collection allows more targeted retrieval but requires API changes. The merged approach is simpler and may be sufficient if the user's queries are specific enough. Consider whether a `source_type` metadata filter on the existing collection could serve both use cases without a second collection.

4. **Chunking for large outputs**: Large repomix outputs will stress the current chunking strategy. If heading-boundary splitting is adopted (ADR-00007), repomix output (which uses `##` headings for each file) would be chunked per-file — which is semantically appropriate. Files that are too long would still need the fixed-size fallback.

5. **Output file location**: If the server generates the repomix output, where should it write it? Options: `.context/repomix-output.md` (committed alongside docs), `~/.mcp-data/repomix/{project}.md` (ephemeral, like ChromaDB), or a temp file (not persisted). The `.context/` location makes it visible and editable but may pollute VCS.

## Decision

TBD — pending resolution of invocation mechanism, storage strategy, and chunking approach (ADR-00007).

## Consequences

TBD

## Alternatives Considered

TBD — to be populated when the decision is made.
