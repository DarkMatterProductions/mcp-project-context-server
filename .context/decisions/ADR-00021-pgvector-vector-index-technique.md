# ADR-00021: pgvector Provider Vector Index Technique

## Status
Under Review

## Context

The server supports three vector store providers (ADR-00015): `chroma-local`, `chroma-http`, and `pgvector`.
ADR-00006 documents the drop-and-recreate indexing strategy used across all providers, but does not address
the underlying vector index technique used within each store.

A review in June 2026 found that no ADR existed for any provider's vector index technique. This ADR fills
that gap for the `pgvector` provider. The ChromaDB providers are covered separately in ADR-00020.

**Current implementation**

The `pgvector` provider creates the following index on each collection table
(`integrations/vectorstore/pgvector/client.py:141`):

```sql
CREATE INDEX IF NOT EXISTS {tbl}_emb_idx ON {tbl} USING ivfflat (embedding vector_cosine_ops)
```

This uses **IVFFlat (Inverted File with Flat compression)** with **cosine similarity** as the distance
operator. This was added during initial implementation of the pgvector provider without formal ADR review
or documented rationale. This ADR exists to formally evaluate and record that decision.

**Index types available in pgvector**

pgvector (0.5.0+) offers three indexing approaches:

1. **No index (sequential scan)**: Exact nearest-neighbour search. PostgreSQL scans the full table on every
   query. Always accurate. Performance degrades linearly with row count. Viable and often preferred for
   small collections.

2. **IVFFlat**: Partitions the vector space into `lists` clusters (default: 100) at build time. Queries
   probe a subset of lists (`probes`, default: 1) to find approximate nearest neighbours. Characteristics:
   - Requires a **minimum row count** to be effective. pgvector's own documentation recommends at least
     `lists * 2` rows before building the index. With the default of 100 lists, this means 200 rows minimum.
     Below this threshold, the PostgreSQL query planner will ignore the index and fall back to a sequential
     scan, making the index a no-op that adds build overhead without benefit.
   - Index must be rebuilt when data changes significantly, as the cluster partitions are computed at build
     time (not dynamically maintained).
   - Under the drop-and-recreate strategy (ADR-00006), the index is rebuilt from scratch on every
     `index_project_context` call, which mitigates stale cluster partitions.

3. **HNSW** (available since pgvector 0.5.0): Graph-based ANN index. Characteristics:
   - No minimum row count. Effective from the first inserted vector.
   - Generally better recall than IVFFlat at equivalent query time.
   - Higher memory usage during index build (`hnsw.ef_construction`, `m` parameters).
   - Available in pgvector 0.5.0 (released September 2023). Most current PostgreSQL deployments with
     pgvector support this version.

**Collection size context**

ADR-00006 describes `.context/` directories as "small by design — typically a handful of markdown files
totaling tens of kilobytes." With heading-boundary chunking (ADR-00007), a typical `.context/` directory
might produce 20–80 chunks. This is well below the 200-row minimum where IVFFlat becomes effective.
In practice, the current IVFFlat index is likely never used by the PostgreSQL query planner for typical
collections, meaning all queries are already executing as sequential scans — but with the overhead of an
index that serves no purpose.

**Options under consideration**

- **Keep IVFFlat (current)**: Accept the existing implementation. For typical collection sizes, the
  index is a no-op and queries fall back to exact sequential scans. Harmless but wasteful; builds an
  unused structure on every re-index.
- **Switch to HNSW**: Better ANN recall, no minimum row count, effective for small and large collections
  alike. Requires pgvector 0.5.0+. Higher memory during build, but the collections indexed here are small
  so build cost is negligible.
- **Remove the index (sequential scan only)**: Exact search with no index build overhead. For the
  collection sizes typical of `.context/` directories, sequential scan is fast and always accurate.
  Loses ANN capability if collections grow significantly in future (e.g. large repomix snapshots,
  ADR-00009).
- **Conditional index**: Build an index only when the collection exceeds a configurable row threshold.
  Adds complexity; not warranted at current scale.

## ADR Review Discussion

**[2026-06-23] James Boylan (Project Owner):** Raised that no ADR exists documenting the vector index
technique for any provider. This was discovered during a discussion with a colleague about indexing strategy.
A separate ADR per provider was requested because not all providers offer the same configurability, and some
cannot be configured at all — this distinction must be explicit in the record.

**[2026-06-23] James Boylan (Project Owner):** Confirmed that the IVFFlat implementation in the pgvector
provider was added without formal review. The intent of this ADR is to formalise the decision. The current
behaviour should remain unchanged until this ADR is accepted, but the correctness of IVFFlat for this use
case should be evaluated during review.

**[2026-06-23] Claude Code (AI Assistant):** Code review of `integrations/vectorstore/pgvector/client.py`
confirms IVFFlat with `vector_cosine_ops` at line 141. No `lists` or `probes` parameters are specified, so
pgvector defaults apply (100 lists, 1 probe). Analysis of collection sizes documented in ADR-00006 and
ADR-00007 indicates that typical `.context/` collections will not reach the 200-row minimum for IVFFlat
to be selected by the PostgreSQL query planner. The index is likely a build-time no-op for almost all
real-world collections this server indexes. HNSW is flagged as the technically stronger alternative:
no minimum row count, better recall, available in pgvector 0.5.0+.

## Decision

[Pending review]

## Consequences

- **IVFFlat is likely inactive for typical collections**: With default `lists=100`, the index requires
  ~200 rows before PostgreSQL will use it. Most `.context/` collections will not reach this threshold,
  meaning queries are already exact sequential scans. The index adds build overhead on every re-index
  without providing query-time benefit.
- **Cosine similarity is explicit**: Unlike the ChromaDB providers (which default to L2), pgvector uses
  cosine similarity via `vector_cosine_ops`. For normalised embedding vectors, the rankings are
  equivalent. The explicit choice here makes the distance metric unambiguous.
- **Index is rebuilt on every re-index**: The drop-and-recreate strategy (ADR-00006) drops and recreates
  the table on each `index_project_context` call, which includes rebuilding the index. This is consistent
  with the overall strategy and avoids stale IVFFlat cluster partitions.
- **If collections grow**: If `.context/` directories grow significantly (e.g. full repomix snapshots
  per ADR-00009), IVFFlat may eventually become effective — but the threshold and recall trade-offs
  should be re-evaluated at that point rather than assumed to be adequate.

## Alternatives Considered

- **HNSW**: No minimum row count, better recall, effective for all collection sizes. Available since
  pgvector 0.5.0. This is the stronger technical choice for this use case and should be evaluated as
  the preferred option during ADR review.
- **No index (sequential scan)**: Exact search, zero build overhead, trivially correct for small
  collections. Loses ANN performance if collections grow into thousands of rows. A viable choice if
  the project's scope remains limited to small `.context/` directories.
- **IVFFlat with tuned `lists` parameter**: Setting `lists` lower (e.g. 10–20) would lower the minimum
  effective row count and reduce build time. Still requires more rows than typical collections contain.
  Adds an operationally configured parameter with no meaningful benefit over HNSW.
- **Conditional index creation**: Create the index only when the collection exceeds a row threshold.
  Adds branching logic to the indexer for a problem better solved by choosing the right index type
  (HNSW) unconditionally. Rejected as unnecessary complexity.
