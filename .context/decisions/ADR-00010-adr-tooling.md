# ADR-00010: ADR tooling design

## Status
Proposed

## Context

`mcp-project-context-server` currently treats `.context/decisions/` as read-only input: ADR files are indexed and searchable, but they can only be created or modified by the user directly in the file system. An LLM agent working on a codebase should be able to participate in the ADR lifecycle — listing existing decisions, reading their content, updating their status, editing their body, and scaffolding new ADRs from the standard template.

This requires a set of new MCP tools. The operations needed are:

- **List ADRs**: Return a summary of all ADR files — number, title, current status — so an agent can quickly see what decisions exist.
- **Read ADR**: Return the full content of a single ADR by number or filename.
- **Update ADR status**: Change the `Status` field of an ADR (e.g., `Proposed` → `Under Review` → `Accepted`). Per the template, the `ADR Review Discussion` section must be removed when status moves to `Accepted`.
- **Edit ADR body**: Update the content of specific sections (Context, Decision, Consequences, Alternatives Considered) without clobbering the entire file.
- **Create ADR**: Scaffold a new ADR file with the next available sequential number, the standard template structure, and `Status: Proposed`.

The ADR template and naming convention are defined in this project (see `project.md` → ADRs section and ADR-00000 template):

- File naming: `ADR-XXXXX-{kebab-case-topic}.md` (5-digit, zero-padded, sequential, never reused)
- Required sections: Status, Context, ADR Review Discussion (Proposed/Under Review only), Decision (Accepted only), Consequences, Alternatives Considered

## ADR Review Discussion

1. **File content manipulation approach**: Should ADR tools operate on raw markdown strings (read the whole file, return or accept full content) or parse and manipulate structured fields? Raw string access is simpler to implement and more flexible. Structured field manipulation (e.g., `update_status`, `update_section`) is more precise and less likely to clobber content accidentally. A hybrid approach — raw read, structured write for known fields — may be the right balance.

2. **Sequential numbering enforcement**: The next ADR number should be determined by scanning `.context/decisions/` for the highest existing number and incrementing. This requires a glob of `ADR-*.md` files and parsing the 5-digit prefix. There must be no gap-filling (if ADR-00003 is deleted, the next ADR is still ADR-00004, not ADR-00003).

3. **Status transition validation**: Should the `update_status` tool validate that transitions are legal (e.g., prevent moving from `Accepted` back to `Proposed`)? Or is the status field treated as a free-text update with no validation? Light validation (warn on unexpected transitions, but don't block) may be the right balance — the agent or user may have legitimate reasons for unusual transitions.

4. **`ADR Review Discussion` section lifecycle**: Per the template, this section is removed when status moves to `Accepted` and the Decision section is finalized. Should the `update_status` tool enforce this automatically (remove the section when status is set to `Accepted`)? Or should this be left to the caller? Automatic enforcement ensures template compliance but reduces transparency about what was in the review discussion.

5. **Tool naming**: Proposed tool names — `list_adrs`, `read_adr`, `create_adr`, `update_adr_status`, `update_adr_section`. These should follow the existing tool naming pattern (snake_case verb-noun).

6. **Re-index after mutation**: ADR tools that write files should trigger (or recommend) a `index_project_context` call to keep the vector store current. This could be done automatically (call the indexer after each write) or left to the caller.

## Decision

TBD — pending resolution of the design questions above.

## Consequences

TBD

## Alternatives Considered

TBD — to be populated when the decision is made.
