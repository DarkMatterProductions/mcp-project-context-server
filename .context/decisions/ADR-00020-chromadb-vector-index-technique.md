# ADR-00020: ChromaDB Vector Index Technique (chroma-local and chroma-http)

## Status
Under Review

## Context

The server supports three vector store providers (ADR-00015): `chroma-local`, `chroma-http`, and `pgvector`.
Two of these — `chroma-local` (ChromaDB `PersistentClient`) and `chroma-http` (ChromaDB `HttpClient`) — are backed
by ChromaDB and share identical indexing behaviour regardless of transport. ADR-00006 documents the
drop-and-recreate indexing strategy used across all providers, but does not address the underlying vector index
technique used within the store itself.

A review in June 2026 found that no ADR existed for any provider's vector index technique. This ADR fills that
gap for the two ChromaDB-backed providers.

**ChromaDB's internal index**

ChromaDB manages its own vector index internally using **Hierarchical Navigable Small World (HNSW)**, an
approximate nearest-neighbour (ANN) graph-based algorithm. This is the only index type ChromaDB supports; it
is not selectable or replaceable through the client API.

HNSW characteristics relevant to this project:
- Graph-based ANN search. Trades exact accuracy for sub-linear query time.
- No training or minimum row count required. Effective from the first inserted vector.
- Index parameters (`hnsw:ef_construction`, `hnsw:M`, `hnsw:ef`, `hnsw:space`) can be supplied as metadata
  keys at collection creation time. Our `create_collection()` calls pass `metadata=metadata or {}` with no
  HNSW-specific keys, so ChromaDB's built-in defaults apply throughout.
- Default distance function is **L2 (squared Euclidean)** unless `hnsw:space` is set to `cosine` or `ip`
  in the collection metadata.

**Why chroma-local and chroma-http are treated as a single ADR**

Both providers call `client.create_collection(name=name, metadata=metadata or {})` with no index
configuration. The ChromaDB server manages the HNSW index in both cases; the transport layer (local file
vs. remote HTTP) has no effect on how vectors are indexed or queried.

**Options considered for HNSW configuration**

ChromaDB does not allow changing the index type. The only decisions available are whether to customise
the HNSW parameters:

- **Accept defaults** (current behaviour): `hnsw:space=l2`, `hnsw:M=16`, `hnsw:ef_construction=100`.
  Appropriate for the small collection sizes typical of `.context/` directories.
- **Set `hnsw:space=cosine`**: Would align the distance metric with the pgvector provider, which uses
  cosine similarity. However, most modern embedding models produce normalised vectors, for which L2
  and cosine produce identical nearest-neighbour rankings. Changing this would require a full re-index
  of all existing collections.
- **Tune `hnsw:M` and `hnsw:ef_construction`**: These control index build quality and memory usage.
  For the expected collection sizes (tens to low hundreds of chunks), defaults are more than adequate.

## ADR Review Discussion

**[2026-06-23] James Boylan (Project Owner):** Raised that no ADR exists documenting the vector index
technique for any provider. This was discovered during a discussion with a colleague about indexing strategy.
ADR-00006 covers the drop-and-recreate lifecycle but does not document the index technique (e.g. HNSW,
IVFFlat, flat scan) used within each provider. This gap must be addressed. A separate ADR per provider was
requested because not all providers offer the same configurability, and some cannot be configured at all —
this distinction must be explicit in the record.

**[2026-06-23] James Boylan (Project Owner):** Confirmed that `chroma-local` and `chroma-http` should be
covered by a single ADR. While they use different transport mechanisms, they are the same underlying provider
(ChromaDB) with identical indexing behaviour. Separating them would produce duplicate ADRs with no meaningful
distinction.

**[2026-06-23] Claude Code (AI Assistant):** Code review of `integrations/vectorstore/chroma_local/client.py`
and `integrations/vectorstore/chroma_http/client.py` confirms that neither provider passes any HNSW
configuration parameters during `create_collection()`. ChromaDB's internal defaults apply. The index type
(HNSW) is not configurable through the ChromaDB client API and therefore cannot be changed at the application
layer. The only configurable aspect is the HNSW tuning parameters via `hnsw:*` collection metadata keys,
none of which are currently set.

## Decision

[Pending review]

## Consequences

- **No control over index type**: ChromaDB's HNSW index is the only available option. This is a constraint
  of the provider, not a project choice.
- **Effective at all collection sizes**: Unlike IVFFlat (see ADR-00021), HNSW does not require a minimum
  number of vectors to be effective. It is appropriate for the small `.context/` collections this server
  indexes.
- **Distance metric is L2 by default**: Nearest-neighbour rankings produced by the ChromaDB providers use
  L2 distance, while the pgvector provider uses cosine similarity. For normalised embedding vectors (the
  common case with modern models), the rankings are equivalent. If unnormalised embeddings are used in
  future, this divergence should be re-evaluated.
- **HNSW parameters are not tuned**: Default parameters are used. This is appropriate for current collection
  sizes but may warrant revisiting if `.context/` directories grow significantly (e.g. large repomix
  snapshots per ADR-00009).
- **No migration required**: Accepting ChromaDB's defaults requires no code changes and no re-indexing of
  existing collections.

## Alternatives Considered

- **Setting `hnsw:space=cosine`**: Would align the distance metric with pgvector. Rejected for now because
  normalised embedding vectors produce equivalent rankings under L2 and cosine, so the practical impact is
  zero. Changing it would require a forced re-index of all existing collections with no user-visible benefit.
  May be reconsidered if a future embedding provider produces unnormalised vectors.
- **Tuning `hnsw:M` or `hnsw:ef_construction`**: Rejected. The default values are well-suited to
  small collections. Tuning adds operational complexity (documented per-provider env vars, migration on
  change) with no measurable benefit at current scale.
- **Switching providers for more configurability**: `pgvector` offers explicit index type selection.
  However, `chroma-local` and `chroma-http` target deployments where PostgreSQL infrastructure is
  unavailable (local developer workflow, lightweight team setups). Replacing them with pgvector to gain
  index control is disproportionate to the need.
