# ADR-00023: GCP Vertex AI Vector Search Provider

## Status
Accepted

## Context

The server supports three vector store providers today (ADR-00015): `chroma-local`, `chroma-http`, and
`pgvector`. Teams already standardised on Google Cloud — particularly those already using the `vertexai`
embedding provider (ADR-00014) — have asked for a vector store backed by **Vertex AI Vector Search**
(formerly "Matching Engine") so the entire embed + store pipeline can run on GCP-native services without
having to stand up or operate PostgreSQL or a ChromaDB HTTP server.

Vertex AI Vector Search differs from the existing providers in two ways that materially affect the design:

1. **Index provisioning is slow and expensive, not instant.** Creating a `MatchingEngineIndex` and deploying
   it to a `MatchingEngineIndexEndpoint` can take tens of minutes to multiple hours, and deployed endpoints
   incur ongoing infrastructure cost regardless of query volume. This is incompatible with the drop-and-recreate
   strategy (ADR-00006), which assumes `create_collection()` can cheaply tear down and rebuild a collection on
   every `index_project_context` call — that assumption holds for a Postgres table or a Chroma collection, but
   not for a Vector Search index.
2. **The FindNeighbors query API returns only datapoint IDs and distances.** Unlike ChromaDB or pgvector,
   Vertex AI Vector Search does not store or return arbitrary document text or metadata dicts alongside a
   vector — it is a pure ANN index. Something else must hold the `document` and `metadata` fields the
   `VectorStoreProvider` Protocol's `upsert`/`query` methods require, keyed by the same IDs used in the index.

**Options considered for index lifecycle:**
- Provider manages index + endpoint creation/deployment programmatically inside `create_collection()`,
  mirroring the drop-and-recreate semantics literally.
- Provider targets a pre-provisioned Index and IndexEndpoint (created out-of-band via Terraform/`gcloud`/
  Console) identified by env-var IDs; `create_collection()` only clears and repopulates datapoints in the
  existing index, and fails clearly if the index/endpoint don't exist.

**Options considered for the document/metadata sidecar:**
- **Firestore** — GCP-native, serverless, shared across processes and machines, requires only enabling the
  API in the same project already used for Vector Search and ADC auth.
- **Reuse a configured `PGVECTOR_CONNECTION_STRING`** purely for the sidecar table, using Vector Search only
  for the ANN index. Avoids a new GCP dependency but forces Postgres to be provisioned even when the whole
  point of this provider is to avoid needing Postgres.
- **Local SQLite file.** Zero extra cloud dependency, but only visible to the process on the machine that
  wrote it — this defeats the multi-instance/shared-team-deployment motivation that justifies choosing a
  cloud vector store in the first place (same motivation documented in ADR-00015's Context for `chroma-http`
  and `pgvector` over `chroma-local`).

**Authentication:** the existing `vertexai` embedding provider (ADR-00014) uses Application Default
Credentials (ADC) exclusively and forces `api_transport="rest"` to avoid a gRPC/asyncio `ProactorEventLoop`
deadlock on Windows (see `integrations/embeddings/vertexai/client.py`). Vertex AI Vector Search's Index/
IndexEndpoint admin operations and the `find_neighbors` query call are both reachable over REST via the
`google-cloud-aiplatform` SDK, so the same constraint and mitigation apply here.

## Decision

Implement `gcp-vector-search` as a fourth `VectorStoreProvider`:

- **Index lifecycle:** the provider targets a **pre-provisioned** Vertex AI Index and IndexEndpoint. It never
  creates, deploys, or deletes GCP infrastructure. `create_collection(name)` removes and re-upserts the
  datapoints for that collection (identified by a metadata restrict/namespace on the deployed index) and
  clears the Firestore sidecar documents for that collection; it does **not** touch the underlying Index or
  IndexEndpoint resources. If the configured Index or IndexEndpoint cannot be found, or no deployment matching
  `GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID` exists on the endpoint, the provider raises `EnvironmentError`/
  `VectorStoreError` with a message that explicitly tells the operator this provider does not provision
  infrastructure and that they must create/deploy the index themselves (via Terraform, `gcloud`, or Console)
  before use.
- **Document/metadata sidecar:** use **Firestore** (`google-cloud-firestore`), one document per datapoint ID
  in a collection named after `GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION` (default derived from the vector store
  collection name), storing `document` and `metadata`. `query()` calls `find_neighbors()` for IDs/distances,
  then batch-reads the corresponding Firestore documents to populate `QueryResult.documents` and
  `.metadatas`.
- **Authentication:** ADC only (`gcloud auth application-default login` / `GOOGLE_APPLICATION_CREDENTIALS`),
  matching the `vertexai` embedding provider. No separate service-account-key-path override is introduced.
- **Transport:** REST, not gRPC, for the same Windows event-loop deadlock reason documented in
  `integrations/embeddings/vertexai/client.py`.
- **Required configuration:** `GCP_VECTOR_SEARCH_PROJECT`, `GCP_VECTOR_SEARCH_LOCATION`,
  `GCP_VECTOR_SEARCH_INDEX_ID`, `GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID`, `GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID`.

## Consequences

- **No accidental infrastructure spend.** Because the provider never creates or deploys indexes/endpoints,
  re-indexing (ADR-00006) cannot trigger the tens-of-minutes-to-hours provisioning latency or the cost of
  spinning up new deployed infrastructure. Operators are fully responsible for capacity planning and initial
  provisioning outside this codebase.
- **New dependency surface.** This provider requires both `google-cloud-aiplatform` (Index/IndexEndpoint
  admin + query) and `google-cloud-firestore` (sidecar). Both ship behind a new `gcp-vector-search` optional
  extra, not bundled into the existing `google-vertex` (embeddings) extra, since a user may want the embedding
  provider without the vector store or vice versa.
- **Two GCP services to operate instead of one.** Teams choosing this provider take on both Vertex AI Vector
  Search and Firestore as dependencies, plus IAM permissions for both. This is more moving parts than
  `pgvector` (single Postgres instance) but avoids operating any non-GCP infrastructure at all.
- **Collection semantics differ subtly from other providers.** `create_collection()` here clears and
  repopulates datapoints/sidecar docs, but the ANN index's build parameters (dimensions, distance measure,
  algorithm config) are fixed at Index-creation time by whoever provisioned it out-of-band. If an operator
  provisions an index with the wrong dimension for the configured `EMBED_PROVIDER`, `upsert()` will fail with
  a clear GCP API error at call time rather than at `create_collection()` time — this should be called out in
  docs as an operator footgun to check before first use.
- **Consistent with the Windows gRPC constraint already documented for `EMBED_PROVIDER=vertexai`.** No new
  incompatibility is introduced beyond what ADR-00015's `INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE` matrix
  already models for the `chroma-*` stores; `gcp-vector-search` uses REST like the vertexai embedding
  provider, so no additional entry is required in that matrix.

## Alternatives Considered

- **Provider manages index lifecycle (auto create/deploy on `create_collection`)**: rejected. Deployment
  latency (tens of minutes to hours) and per-deployment cost make it unsafe to trigger from a call pattern
  (`index_project_context`) that other providers treat as cheap and frequent. An operator could unknowingly
  re-trigger expensive infrastructure changes on every re-index.
- **Reuse `PGVECTOR_CONNECTION_STRING` for the sidecar**: rejected as the default. It would force every
  `gcp-vector-search` deployment to also provision and operate PostgreSQL, defeating the goal of a fully
  GCP-native pipeline. (Not precluded as a future configurable alternative if a team already runs Postgres
  and prefers not to add Firestore — but out of scope for this ADR.)
- **Local SQLite sidecar**: rejected. Only visible to the process/machine that wrote it, which breaks the
  shared/multi-instance deployment model that is the core motivation for choosing a cloud vector store over
  `chroma-local` in the first place (ADR-00015).
- **gRPC transport**: rejected for the same reason `EMBED_PROVIDER=vertexai` forces REST — gRPC's C-core
  polling engine can deadlock when it shares a process with asyncio's `ProactorEventLoop`, which this server
  requires on Windows for stdio subprocess support.
