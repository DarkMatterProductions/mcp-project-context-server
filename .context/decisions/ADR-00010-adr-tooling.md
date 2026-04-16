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

1. **File content manipulation approach**: Option C is selected. `read_adr` returns the full ADR markdown in raw form, while targeted reads and writes (`read_adr_status`, `list_adr_sections`, `search_adr_sections`, `read_adr_section`, `update_adr_status`, `update_adr_section`) use structured section parsing. This keeps read and write behavior aligned while reducing unrelated content retrieval.

2. **Sequential numbering enforcement**: Option A is selected. `create_adr` acquires a lock in `.context/decisions/`, scans valid `ADR-XXXXX-*.md` files, allocates `max(existing_number) + 1`, and creates the new ADR file atomically before releasing the lock. Number parsing uses only strict 5-digit ADR filenames; malformed filenames are ignored for allocation and returned as warnings. If no valid ADR files exist, allocation starts at `ADR-00001`. There is no gap-filling and no number reuse.

3. **Status transition validation**: Option 3 is selected. `update_adr_status` performs light validation against known status values and expected transition flow, and returns warnings for unusual transitions rather than blocking them. For any unusual transition, the caller must provide an explanation. While the ADR is in `Proposed` or `Under Review`, the tool records the explanation in `ADR Review Discussion`. If the status transition moves the ADR to `Accepted`, the tool preserves the explanation in the `Decision` section as transition rationale.

4. **`ADR Review Discussion` section lifecycle**: Option A is selected. `update_adr_status` enforces this automatically when status is set to `Accepted`: it requires a populated `Decision` section, preserves any required transition rationale in `Decision`, removes the `ADR Review Discussion` section, and then writes `Status: Accepted`. If these preconditions are not met, the transition to `Accepted` fails with an actionable error.

5. **Tool naming**: Option 1 is selected, with section-tool scope clarified. ADR tooling follows the existing project naming style (`{action}_{subject}` / verb-noun) and uses: `list_adrs`, `read_adr`, `read_adr_status`, `list_adr_sections`, `search_adr_sections`, `read_adr_section`, `search_adrs`, `create_adr`, `update_adr_status`, `update_adr_section`. The section-tool names are explicitly ADR-scoped because section operations are single-ADR actions.

6. **Re-index after mutation**: Option C is selected. ADR write tools (`create_adr`, `update_adr_status`, `update_adr_section`) do not auto-reindex by default, and responses indicate that reindexing is required to refresh vector search results. Write tools support an optional `auto_reindex` flag to trigger `index_project_context` when immediate freshness is needed. This avoids forcing full reindex cost on every write while preserving an opt-in strong-consistency path.

7. **`search_adrs` scope and implementation**: Option B is selected. `search_adrs` uses the existing ChromaDB vector store and embedding pipeline, with ADR-scoped filtering so only `.context/decisions/` content is returned. This keeps ADR search semantic, consistent with project-wide search behavior, and aligned with the purpose of indexing. Because this depends on index freshness, responses should surface stale or missing index conditions with clear guidance to run `index_project_context` (or use `auto_reindex` during write flows when immediate freshness is required).

8. **`search_sections` implementation**: Option B is selected. `search_adr_sections` uses vector-based search with filters that constrain results to chunks within the selected ADR section scope. This aligns with the planned header-based chunking strategy so semantic retrieval can remain section-aware while still leveraging embeddings. As with other vector-backed tools, responses should provide clear stale-index guidance when reindexing is required.

9. **Session checkpoint (2026-04-15)**: Review paused by request. Questions 1 through 8 are resolved and recorded above. Remaining work on return: (a) populate `## Decision` with the finalized design summary based on Q1-Q8 outcomes, (b) populate `## Consequences` with implementation and operational impacts, (c) populate `## Alternatives Considered` with rejected options, and (d) continue lifecycle progression after content review (`Proposed` -> `Under Review` or `Accepted` when finalization criteria are met).

## Decision

TBD — pending resolution of the design questions above.

## Consequences

TBD

## Alternatives Considered

TBD — to be populated when the decision is made.
