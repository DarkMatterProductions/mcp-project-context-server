# ADR-00030: Incremental upsert-then-prune indexing via content-addressed chunk IDs

## Status

Accepted

## Context

This supersedes ADR-00006 (Drop-and-recreate indexing).

Prior to the all-or-nothing reorder now documented in ADR-00006's Consequences section, `run_index_pipeline()` cleared a project's existing chunks *before* attempting to embed their replacements. Observed on 2026-09-21 against a live collection (`ctx_deep_space_logistics_automation`): two consecutive `index_project_context` runs over **unchanged** source content shrank the collection from 33 to 31 chunks, permanently destroying 4 previously good chunks — including the top-ranked search hit for a query run minutes earlier (`project.md`'s `## Architecture` section, containing the project's requirement definitions and a DECIDED architecture statement). After the loss, the same query silently returned a weaker, incomplete neighboring chunk; nothing in the tool's reported output indicated anything had been lost. Because the trigger was embedding-provider failures (rate limits, timeouts) rather than anything content-related, the specific chunks destroyed varied run to run — re-running the tool, the obvious operator remedy for a partial failure, could make the index strictly worse rather than better. The fix reordered the pipeline so `run_index_pipeline()` now embeds every chunk before touching the store at all, aborting with zero store writes if any chunk fails to embed, closing the destructive window entirely.

That fix closed the data-loss hole, but it left a cost problem: every call to `index_project_context` still re-embeds and rewrites the *entire* collection, even when nothing in `.context/` changed since the last run. This is because chunk IDs were positional (`f"{filename}::{chunk_idx}"`) and carried no information about the chunk's content — an unchanged chunk got a "new" ID on every run purely because it was assigned by position, so the indexer had no way to tell what actually changed without re-embedding everything and diffing after the fact.

Options considered:

1. **Keep drop-and-recreate, accept the cost.** The `.context/` directories indexed by this server are small (a handful of markdown files, tens of kilobytes), so a full rebuild is fast in wall-clock terms. But "fast" is not the same as "cheap" for embedding providers: every rebuild re-spends embedding-provider tokens/quota on unchanged content, which matters for metered or rate-limited providers (e.g. Voyage AI's free tier). This cost scales with `.context/` size and call frequency, and is wasted on the common case where a session calls `index_project_context` repeatedly with little or no actual content drift.

2. **Incremental update via a file-hash manifest.** ADR-00006 already flagged this as a rejected alternative "for now," citing the complexity of maintaining a separate manifest of file hashes and chunk IDs alongside the vector store's own state — a second source of truth that can drift from the store itself (e.g. if a write partially fails, or the manifest file is edited/deleted out of band).

3. **Content-addressed chunk IDs (chosen).** Derive each chunk's ID directly from its content (file, section header, and a SHA-512 hash of the section's text) rather than from its position in the file. An unchanged chunk always re-derives the *same* ID on every run, so diffing the store's existing ID set against the freshly computed expected ID set — a single `list_ids()` call — is sufficient to determine exactly what changed, with no separate manifest to maintain and no drift risk (the vector store itself is the only source of truth). This also lets the indexer embed only the IDs that are new, skipping the embedding-provider call entirely for unchanged content.

4. **Timestamp-based incremental update.** Rejected in ADR-00006 already, for the same reasons that apply here: file modification times are unreliable across OS restarts, VCS checkouts, and some editors, and would miss content-only changes where mtime is preserved.

A secondary benefit of option 3: it generalizes the all-or-nothing guarantee from ADR-00006 to per-chunk granularity. Because replaced content always gets a *new* ID (derived from its new hash), there is never a window where old and new content for the same logical chunk overlap destructively — the old ID simply becomes eligible for pruning once the new ID's chunk is confirmed embedded and upserted.

## Decision

**Incremental upsert-then-prune indexing**, replacing drop-and-recreate as the strategy used by `run_index_pipeline()` (ADR-00006's `create_collection`/`delete_collection` remain available as Protocol API but are no longer called by the indexer).

**Chunk ID scheme:**

```
f"{filename}::{header}::{segment}-{section_sha512}"
```

- `header` is `section.name` from `split_sections()`.
- `segment` is the sub-chunk index within `chunk_section(section, max_chars)`, reset to `0` per section.
- `section_sha512` is `hash_content(section.content)`, computed once per section and shared by all of that section's sub-chunks.

Chunks are deduped by ID before any further processing (first occurrence kept, collision logged as a warning), guaranteeing no batch handed to a backend's `upsert` can contain a duplicate ID.

**Algorithm**, on each `index_project_context` call:

1. Build all chunks for the current `.context/` state and compute `expected_ids = {c.id for c in all_chunks}`.
2. Fetch `existing_ids = set(await store.list_ids(col_name))`.
3. Compute `to_embed = [c for c in all_chunks if c.id not in existing_ids]` and `to_delete = sorted(existing_ids - expected_ids)`.
4. Embed only `to_embed`, using the existing semaphore-bounded concurrent embedding path. If any embed fails, abort immediately with zero calls to `ensure_collection`, `upsert`, or `delete_by_ids` — the existing collection is left untouched — and return a status message naming every failed chunk's file and section, and stating explicitly that the collection was not modified and the previous index remains available.
5. On full embedding success: call `store.ensure_collection(col_name, metadata=collection_metadata)` unconditionally (refreshes provenance metadata even on a true no-op run), then `store.upsert(...)` for `to_embed` only if non-empty, then `store.delete_by_ids(col_name, to_delete)` only if non-empty.
6. Return a status message reporting chunks embedded, chunks unchanged, and chunks removed.

**New `VectorStoreProvider` Protocol methods**, implemented identically in behavior (though not in mechanism) across all four backends (chroma_local, chroma_http, pgvector, gcp_vector_search):

- `ensure_collection(name, metadata=None)`: create the collection if absent; if present, refresh its metadata in place without touching existing documents. Non-destructive counterpart to `create_collection`.
- `list_ids(collection_name)`: every document ID currently stored; `[]` if the collection doesn't exist.
- `delete_by_ids(collection_name, ids)`: remove the given IDs; no-op for an empty list or unknown IDs.

The zero-chunks case (e.g. an empty `.context/`) is not special-cased: with `all_chunks` empty, `to_embed` is empty and `to_delete` is every existing ID, so the general algorithm correctly prunes everything.

Migration from the old positional ID scheme (`f"{filename}::{chunk_idx}"`) requires no special code: the old and new ID formats share zero string overlap by construction, so the first post-upgrade run naturally treats every existing document as stale and every current chunk as new — a one-time full convergence, then incremental from then on.

## Consequences

- **Cheaper no-op and partial re-indexes**: A re-index with no content changes calls the embedding provider zero times — `list_ids()` diffed against the freshly computed expected ID set shows nothing new and nothing stale. A partial change (one file edited) only embeds the chunks whose content-derived ID isn't already present in the store. This directly reduces embedding-provider token/quota spend and exposure to rate limits for metered providers.
- **Per-chunk all-or-nothing, not just per-run**: Because a changed chunk always gets a new ID, there is never a window where old and new content for the same logical chunk coexist destructively. The old ID becomes eligible for pruning (via `delete_by_ids`) only after the new ID's chunk has been successfully embedded and upserted. Embedding still happens before any store write, and any embed failure aborts the run with zero calls to `ensure_collection`, `upsert`, or `delete_by_ids` — the previously indexed collection is left completely intact, generalizing ADR-00006's existing all-or-nothing guarantee to the smaller `to_embed` subset.
- **One-time full convergence on upgrade**: The first run after upgrading from the old positional ID scheme treats every existing document as stale (since old and new IDs never overlap) and every current chunk as new, so it pays a one-time full re-embed cost equivalent to today's drop-and-recreate behavior. Every run after that is incremental.
- **New required Protocol surface**: All four `VectorStoreProvider` backends (chroma_local, chroma_http, pgvector, gcp_vector_search) must implement `ensure_collection`, `list_ids`, and `delete_by_ids` in addition to the existing `create_collection`/`delete_collection`. `create_collection`'s destructive drop-and-recreate contract is unchanged and remains available as API surface, but the indexer no longer calls it.
- **Provenance metadata is refreshed independent of content drift**: `ensure_collection(name, metadata=...)` is called on every successful run, even a true no-op, so `indexed_at` reflects "last time indexing was run" rather than "last time content changed." Callers that want to detect actual content drift must compare document IDs or counts, not just `indexed_at`.
- **Accepted limitation — duplicate-header collision**: Two sections in the same file with an identical header name and byte-identical content produce the same chunk ID and are deduplicated to a single chunk (first occurrence kept, a warning logged). This is considered rare and harmless; it is not disambiguated further (e.g. no positional tiebreaker added to the ID).
- **Supportability**: `list_ids`/`delete_by_ids` are read/delete primitives with straightforward per-backend implementations (a metadata-only `get`/`delete` for Chroma, a SQL `SELECT`/`DELETE` for pgvector, a Firestore sidecar read/set-difference for GCP Vector Search). Backends differ in failure behavior on these calls — chroma_local, chroma_http, and pgvector swallow exceptions from `ensure_collection`/`delete_by_ids` and behave as a no-op, while gcp_vector_search raises `VectorStoreError`. This asymmetry existed before this change (in `create_collection`/`delete_collection`) and is preserved rather than newly introduced.
- **No memory ceiling on the embed phase**: Like ADR-00006's all-or-nothing guarantee, this design holds every to-be-embedded chunk's embedding in memory for the duration of a run, before writing anything to the store. This is a non-issue at today's `.context/` sizes (tens of kilobytes across a handful of files) but has no streaming or batching ceiling; a very large repository could in principle exhaust memory during the embed phase before ever reaching `ensure_collection`/`upsert`. Flagged as a known limitation, not yet addressed — revisit if `.context/` sizes grow substantially (see ADR-00009).

## Alternatives Considered

- **Keep drop-and-recreate as-is (status quo)**: Rejected. Correct and simple, but every `index_project_context` call re-embeds and rewrites the entire collection regardless of whether anything changed, wasting embedding-provider tokens/quota on unchanged content on every run — a real cost for metered or rate-limited providers, not just a theoretical one.
- **File-hash manifest for incremental updates**: Rejected, per ADR-00006's own prior rejection of this approach. Requires maintaining a second source of truth (a manifest of file hashes and chunk IDs) alongside the vector store's actual state, which can drift from the store if a write partially fails or the manifest is edited/deleted out of band. Content-addressed IDs make the vector store itself the only source of truth — `list_ids()` is always authoritative.
- **Timestamp-based incremental update**: Rejected, per ADR-00006's own prior rejection. File modification times are unreliable across OS restarts, VCS checkouts, and some editors, producing false positives and missing content-only changes when mtime is preserved.
- **Disambiguating duplicate-header collisions with a positional tiebreaker**: Considered and rejected as unnecessary complexity. Two sections with an identical header and byte-identical content are, by definition, interchangeable for indexing/retrieval purposes — deduplicating to one chunk loses nothing a reader would notice.
