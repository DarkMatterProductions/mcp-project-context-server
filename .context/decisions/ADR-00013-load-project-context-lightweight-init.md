# ADR-00013: Lightweight session initialization for load_project_context

## Status
Proposed

## Context

`load_project_context` is called at the start of every session (enforced by `CLAUDE.md`). Its current behavior is to return three things in one response:

1. The full content of `project.md`
2. The full content of every ADR file in `.context/decisions/`
3. The most recent session summary

This design assumes that an agent needs all of this information upfront. In practice, the response size scales linearly with the number and size of ADR files. For this project — 11 ADRs at time of writing — the response was 56.2 KB and could not be read in full within the agent's context window. The agent fell back to direct file system reads, bypassing the tool entirely and defeating its purpose.

The problem compounds over time: as the project accumulates ADRs, the tool becomes progressively less useful. A project with 30 ADRs will produce a response three times larger than today's.

The root issue is that the tool's mandate conflates two distinct operations:

- **Session orientation** — give the agent enough context to understand what project it is in, what it is for, and what work is currently active. `project.md` serves this need precisely. It is bounded in size and contains the information an agent needs to orient itself.
- **Deep reference access** — retrieve the full content of specific ADRs, past decisions, or historical context. This is an on-demand need that varies by task. Most sessions do not require reading all ADRs.

The solution is to reduce `load_project_context` to its essential function: return `project.md` and nothing else. ADR content should be fetched on demand using the tools introduced in ADR-00012 (`read_adr`, `search_adr`). To support this, `load_project_context` should also return a lightweight ADR index — number, title, status, filename — so the agent knows what decisions exist and can fetch those relevant to its current task.

The session summary can be retained as an optional element: if a recent session summary exists, include it (it is typically short). If it is long or absent, omit it.

## ADR Review Discussion

[Discussion pending]

## Decision

[Pending review]

## Consequences

- `load_project_context` response size becomes bounded by the size of `project.md` plus the ADR index, rather than by the total size of all ADR files. Response size growth is decoupled from ADR count.
- Agents that previously relied on `load_project_context` to deliver full ADR content must now call `read_adr` or `search_adr` explicitly. This is a breaking change in behavior but not in the tool's interface signature.
- The ADR index returned by `load_project_context` (number, title, status, filename) gives the agent enough information to decide which ADRs are relevant to its current task before fetching their full content.
- Session orientation becomes reliable regardless of project size or ADR count — `load_project_context` will always succeed within context limits.
- The `CLAUDE.md` instruction to call `load_project_context` at session start remains valid and sufficient. No change to the per-project hook is required.
- The tools introduced in ADR-00012 (`read_adr`, `search_adr`, `read_project`) must be implemented before or alongside this change, as they are the primary access path for content that `load_project_context` no longer returns.

## Alternatives Considered

**Paginate `load_project_context` output**: Allow callers to request ADRs in pages or by status filter. Reduces response size but adds complexity to the call site, and still requires the agent to make multiple calls to get full coverage. Does not solve the fundamental mismatch between bulk delivery and selective need.

**Compress or summarize ADR content**: Return only the `## Status` and first paragraph of each ADR rather than the full text. Reduces size but loses fidelity — the agent may act on a summary that omits a critical constraint or alternative. On-demand access via `read_adr` is strictly better.

**Raise the response size limit**: Does not address the root cause. The agent's context window is finite regardless of any server-side limit. Larger responses consume context that could be used for the actual task.

**Keep current behavior; add `load_project_context_slim` as a separate tool**: Avoids a breaking change but creates two tools with overlapping purpose. Callers must decide which to use, and the default (`load_project_context`) remains broken for large projects. Fixing the existing tool is preferable to fragmenting the interface.
