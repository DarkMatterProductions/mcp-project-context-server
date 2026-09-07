# ADR-00029: Watchdog-based auto-reindex

## Status
Proposed

## Context

This sub-item was originally raised as an open extension inside ADR-00006's ADR Review Discussion — it was never tracked as its own ADR. ADR-00006 chose drop-and-recreate as the indexing strategy for `index_project_context`, but also considered whether indexing should trigger automatically when `.context/` files change on disk, rather than requiring an explicit tool call. The `watchdog` library provides cross-platform file system event monitoring and was already present in `requirements.txt` in anticipation of this feature.

If implemented, it would watch the `.context/` directory for file creation, modification, and deletion events and trigger a debounced re-index automatically.

As of this writing, this remains unimplemented: there is no `watchdog` usage anywhere in `src/`.

## ADR Review Discussion
[Discussion pending]

## Decision
[Pending review]

## Consequences

- Rapid successive file saves (e.g. editor autosave) would need to be debounced to avoid triggering redundant full rebuilds, since each rebuild is a full drop-and-recreate (ADR-00006).
- Would require a background file-watcher process/thread alongside the MCP server, an operational component that does not exist today.
- Would remove the need for an explicit `index_project_context` call after every `.context/` edit, at the cost of the added complexity above.

## Alternatives Considered

- **Manual trigger only (status quo)**: this is the current behavior per ADR-00006 — `index_project_context` must be called explicitly. Simple and predictable, but requires the caller to remember to re-index after editing `.context/`.
