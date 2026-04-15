# ADR-00012: Targeted tools for ADR and project.md access

## Status
Proposed

## Context

`load_project_context` currently returns the full content of `project.md`, all ADR files, and the latest session summary in a single response. In practice this output regularly exceeds what can be held in an LLM's active context window — the tool response for this project was 56.2 KB, which had to be saved to a temp file and could not be read in full. The calling agent silently fell back to direct file system reads to answer a basic question about the project's ADRs.

This is a structural problem: a tool designed as the primary session entry point is producing output that cannot be consumed by the agent it is designed to serve. The root cause is that the tool couples *session initialization* (load `project.md` so the agent knows what project it is in) with *bulk content delivery* (return every ADR verbatim). These are two distinct needs and should not be handled by the same operation.

The solution is a set of targeted, single-purpose tools that allow an agent to fetch exactly what it needs, when it needs it — rather than receiving everything upfront and hoping it fits in context. The required tools are:

**ADR tools:**
- `read_adr` — return the full content of a single ADR by number or filename
- `write_adr` — create or fully overwrite an ADR file (handles sequential number assignment when creating)
- `edit_adr` — update a specific section of an existing ADR without touching the rest of the file
- `search_adr` — search ADR content by keyword or semantic query; returns matching excerpts and file references

**Project tools:**
- `read_project` — return the full content of `project.md`
- `write_project` — fully replace `project.md`
- `edit_project` — update a specific section of `project.md` without touching the rest of the file

ADR-00010 proposed a related set of ADR lifecycle tools (`list_adrs`, `read_adr`, `create_adr`, `update_adr_status`, `update_adr_section`) but left key design questions unresolved. This ADR incorporates the `project.md` tools (not covered in ADR-00010) and narrows the tool set to the operations that directly address the context-overflow problem. The naming and interface here supersede the proposals in ADR-00010.

## ADR Review Discussion

[Discussion pending]

## Decision

[Pending review]

## Consequences

- Agents can retrieve ADR and project content on demand rather than receiving it all at once, eliminating context overflow on projects with large or numerous context files.
- `write_adr` must enforce the sequential numbering convention (scan `.context/decisions/` for the highest existing number, increment, zero-pad to 5 digits) to prevent gaps or duplicates.
- `edit_adr` and `edit_project` must operate on named sections (e.g., `## Context`, `## Decision`) rather than line numbers or byte offsets, so edits remain valid as file content changes.
- `search_adr` requires that `index_project_context` has been run; callers must handle the case where the index is stale or absent.
- Any tool that writes a file should return a recommendation (or automatically trigger) `index_project_context` to keep the vector store current.
- Clients that currently rely on `load_project_context` returning full ADR content will need to migrate to calling `read_adr` or `search_adr` explicitly.

## Alternatives Considered

**Increase the output limit on `load_project_context`**: Does not solve the problem — it shifts the overflow threshold rather than eliminating it. A project with 50 ADRs will overflow any fixed limit.

**Return only ADR summaries (title + status) from `load_project_context`**: Reduces output size but still couples initialization with content delivery. An agent that needs no ADR context still pays the cost of fetching all summaries.

**Expose raw file system tools (read_file, write_file)**: Overly general — agents would need to know `.context/` directory structure, naming conventions, and template requirements. Purpose-built tools encode these conventions and reduce the surface area for mistakes.

**Extend `search_project_context`**: The existing search tool operates over the vector index, which is appropriate for semantic queries. Direct read/write/edit operations require deterministic file access, not vector similarity — these are different enough to warrant separate tools.
