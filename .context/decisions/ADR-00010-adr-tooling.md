# ADR-00010: ADR tooling design

## Status
Proposed

## Context

`mcp-project-context-server` currently treats `.context/decisions/` as read-only input: ADR files are indexed and searchable, but they can only be created or modified by the user directly in the file system. An LLM agent working on a codebase should be able to participate in the ADR lifecycle — listing existing decisions, reading their content, updating their status, editing their body, and scaffolding new ADRs from the standard template.

This requires a set of new MCP tools. The operations needed are:

- **List ADRs**: Return a summary of all ADR files — number, title, current status — so an agent can quickly see what decisions exist.
- **Read ADR**: Return the full content of a single ADR by number or filename in its raw, unprocessed markdown form.
- **Read ADR Status**: Return only the `Status` field of a single ADR — a lightweight check without loading the full file content.
- **List Sections**: Return the section tree for a selected ADR, including nested section paths represented as ordered arrays (for example, `["Context", "Constraints"]`).
- **Search Sections**: Search sections within a selected ADR only (no cross-ADR mode) and return matching section paths and excerpts.
- **Read ADR Section**: Return the content of a specific section in a selected ADR, including nested sections addressed by an ordered array path (for example, `["Context", "Constraints"]`).
- **Search ADRs**: Perform a targeted search within ADR files only — by keyword, status, or semantic query — returning matching ADR summaries or excerpts.
- **Update ADR status**: Change the `Status` field of an ADR (e.g., `Proposed` → `Under Review` → `Accepted`). Per the template, the `ADR Review Discussion` section must be removed when status moves to `Accepted`.
- **Edit ADR body**: Update the content of specific ADR sections without clobbering the entire file, including nested sections addressed by ordered array paths.
- **Create ADR**: Scaffold a new ADR file with the next available sequential number, the standard template structure, and `Status: Proposed`.

The ADR template and naming convention are defined in this project (see `project.md` → ADRs section and ADR-00000 template):

- File naming: `ADR-XXXXX-{kebab-case-topic}.md` (5-digit, zero-padded, sequential, never reused)
- Required sections: Status, Context, ADR Review Discussion (Proposed/Under Review only), Decision (Accepted only), Consequences, Alternatives Considered

## ADR Review Discussion

1. **File content manipulation approach**: Option C is selected. `read_adr` returns the full ADR markdown in raw form, while targeted reads and writes (`read_adr_status`, `list_sections`, `search_sections`, `read_adr_section`, `update_adr_status`, `update_adr_section`) use structured section parsing. This keeps read and write behavior aligned while reducing unrelated content retrieval.

2. **Sequential numbering enforcement**: The next ADR number should be determined by scanning `.context/decisions/` for the highest existing number and incrementing. This requires a glob of `ADR-*.md` files and parsing the 5-digit prefix. There must be no gap-filling (if ADR-00003 is deleted, the next ADR is still ADR-00004, not ADR-00003).

3. **Status transition validation**: Should the `update_status` tool validate that transitions are legal (e.g., prevent moving from `Accepted` back to `Proposed`)? Or is the status field treated as a free-text update with no validation? Light validation (warn on unexpected transitions, but don't block) may be the right balance — the agent or user may have legitimate reasons for unusual transitions.

4. **`ADR Review Discussion` section lifecycle**: Per the template, this section is removed when status moves to `Accepted` and the Decision section is finalized. Should the `update_status` tool enforce this automatically (remove the section when status is set to `Accepted`)? Or should this be left to the caller? Automatic enforcement ensures template compliance but reduces transparency about what was in the review discussion.

5. **Tool naming**: Proposed tool names — `list_adrs`, `read_adr`, `read_adr_status`, `list_sections`, `search_sections`, `read_adr_section`, `search_adrs`, `create_adr`, `update_adr_status`, `update_adr_section`. These should follow the existing tool naming pattern (snake_case verb-noun).

6. **Re-index after mutation**: ADR tools that write files should trigger (or recommend) a `index_project_context` call to keep the vector store current. This could be done automatically (call the indexer after each write) or left to the caller.

7. **`search_adrs` scope and implementation**: The `search_adrs` tool targets ADR files specifically, whereas `search_project_context` searches the entire indexed `.context/` collection. Should `search_adrs` operate directly on the filesystem (e.g., grep/regex over ADR filenames and content) for simplicity, or query the existing ChromaDB vector store with an ADR-scoped filter for semantic capability? A filesystem approach requires no vector store dependency but is limited to keyword/status matching. A vector store approach enables semantic search but requires the index to be current.

8. **`search_sections` implementation**: `search_sections` is scoped to a selected ADR only. Should it operate directly on the ADR file (heading-aware text search) for deterministic behavior, or leverage vector search over that ADR's indexed chunks for semantic matching? File-based search has no index freshness dependency but weaker semantic recall. Vector search has better semantic recall but depends on re-indexing.

## Decision

TBD — pending resolution of the design questions above.

## Consequences

TBD

## Alternatives Considered

TBD — to be populated when the decision is made.
