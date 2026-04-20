# ADR-00006: Drop-and-recreate indexing with planned watchdog auto-reindex

## Status
Implemented (drop-and-recreate on manual trigger)
Proposed (watchdog-based auto-reindex)

## Context

When `index_project_context` is called, the server must update the ChromaDB collection to reflect the current state of `.context/`. Two broad strategies were considered:

**Incremental update:**
- Read the current collection state (existing document IDs and their source files)
- Detect which files have been added, modified, or deleted since the last index
- Add new chunks, update changed chunks, delete stale chunks
- Leaves the collection in a queryable state at all times

**Drop and recreate:**
- Delete the entire collection
- Rebuild from scratch: read all files, chunk, embed, and batch-add
- Simpler implementation with no change-tracking logic
- The collection is unavailable (or partially populated) during the rebuild

The `.context/` directories indexed by this server are small by design — typically a handful of markdown files totaling tens of kilobytes. Full rebuild time is negligible for this data volume.

A secondary question was whether indexing should be triggered automatically when `.context/` files change on disk, rather than requiring an explicit `index_project_context` tool call. The `watchdog` library (already in `requirements.txt`) provides cross-platform file system event monitoring.

## Decision

**Drop-and-recreate** was chosen for the `index_project_context` implementation. On each call:

1. The ChromaDB collection for the project is deleted (if it exists)
2. A new empty collection is created with the same name
3. All `.md` files in `.context/` are read, chunked, and embedded
4. All valid embeddings are batch-added in a single call

This is implemented in `indexing/chroma/indexer.py` via `index_project_context(project_path)`.

`watchdog`-based auto-reindex is planned but not yet implemented. When added, it will watch the `.context/` directory for file creation, modification, and deletion events and trigger a debounced re-index automatically.

## Consequences

- **Simplicity**: No change-tracking, no stale entry cleanup, no file hash manifest. The implementation is straightforward and correct by construction.
- **Correctness on renames/deletes**: Files that are renamed or deleted are automatically excluded from the next index — no explicit deletion logic is needed.
- **Collection unavailability during rebuild**: Between the drop and the final batch-add, the collection contains no documents. A `search_project_context` call during this window will return zero results. For the typical use case (manual trigger, small dataset, fast rebuild), this window is negligible.
- **No partial-failure recovery**: If the embed step fails mid-way through a large index operation, the collection is left empty. The user must call `index_project_context` again. Individual chunk embedding failures are logged and skipped rather than aborting the entire operation.
- **Watchdog debouncing**: When the auto-reindex feature is implemented, rapid successive file saves (e.g., editor autosave) must be debounced to avoid triggering redundant full rebuilds.

## Alternatives Considered

- **Incremental update by file hash**: Rejected for now. Requires maintaining a manifest of file hashes and chunk IDs. Adds significant complexity for a dataset size where full rebuild is fast. May be reconsidered if `.context/` directories grow to contain large repomix snapshots (see ADR-00009).
- **Timestamp-based incremental update**: Rejected. File modification times are unreliable across OS restarts, VCS checkouts, and some editors. Would produce false-positives and miss content-only changes if mtime is preserved.
