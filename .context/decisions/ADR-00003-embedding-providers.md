# ADR-00003: Ollama-first embedding with planned cloud provider extensibility

## Status
Accepted (Ollama as initial provider)
Proposed (cloud provider support)

## Context

The server requires an embedding provider to convert text chunks into vector representations for ChromaDB indexing and query similarity search. The options considered were:

- **Ollama (local)**: Runs embedding models locally via the Ollama API. No API key, no cost, no data leaves the machine. Requires Ollama to be running locally with the desired model pulled. The `ollama` Python library provides both sync and async clients.
- **OpenAI Embeddings API**: High-quality embeddings (`text-embedding-3-small`, `text-embedding-3-large`). Requires an API key and sends text data to OpenAI's servers. Per-token cost.
- **Cohere Embed API**: Strong embedding quality, particularly for retrieval tasks. Requires an API key and sends data off-device.
- **Google Gemini Embeddings**: Cloud-based, high quality. Requires a Google API key and sends data off-device.
- **HuggingFace sentence-transformers (local)**: Can run locally without Ollama. Requires a Python ML dependency stack (`torch`, `transformers`, etc.) — significantly heavier than the current dependency footprint.

The original project goal was full local LLM support throughout the stack. Project context files (documentation, ADRs, session notes) may contain sensitive architectural or business information. Keeping embeddings local avoids data leakage, API costs, and internet connectivity requirements.

At the same time, cloud embedding providers offer higher model quality and may be preferred in environments where the data sensitivity concern does not apply.

## Decision

Ollama was chosen as the initial and sole embedding provider. The default model is `nomic-embed-text`, configurable via the `EMBED_MODEL` environment variable. The Ollama host is configurable via `OLLAMA_HOST` (default: `http://localhost:11434`).

The integration is isolated behind `integrations/ollama/` so that the `tools/` and `indexing/` layers have no direct provider dependency. Both sync (`get_embedding`) and async (`get_embedding_async`) interfaces are provided in `integrations/ollama/client.py`. The `indexing/ollama/embedder.py` module provides thin named wrappers (`embed_chunk`, `embed_chunk_async`) for semantic clarity in the indexing pipeline.

Cloud provider support is planned as a configurable extension (see ADR Review Discussion below). The `integrations/` structure is designed to accommodate a provider abstraction.

## Consequences

- The default setup requires Ollama to be running locally with `nomic-embed-text` pulled (`ollama pull nomic-embed-text`). Without this, `index_project_context` and `search_project_context` will fail.
- The `integrations/` layer must remain provider-agnostic as cloud support is added. Tool handlers and indexing logic must not import from `integrations/ollama/` directly — they must go through `indexing/ollama/embedder.py` or a future abstract interface.
- Switching embedding providers requires re-indexing: embeddings from different models are not comparable. Any `EMBED_MODEL` or provider change should be followed by a call to `index_project_context` to rebuild the collection.

## Alternatives Considered

- **OpenAI / Cohere / Gemini embeddings (cloud only)**: Rejected as the sole option. The local-first goal requires that the server function without internet access or API keys. Cloud providers remain viable as opt-in alternatives once a provider abstraction is introduced.
- **HuggingFace sentence-transformers**: Rejected. While local, the dependency footprint (`torch`, `transformers`, CUDA/CPU build variants) is disproportionate for this server's use case and would significantly complicate installation.

## ADR Review Discussion

**Cloud provider extension (Proposed):**

The following design questions are open and must be resolved before cloud provider support is implemented:

1. **Provider selection mechanism**: Should the provider be selected via an env var (e.g., `EMBED_PROVIDER=openai`) or via the planned YAML config file (ADR-00005)? The env var approach is simpler; YAML config would allow per-project provider overrides.

2. **Common interface**: All providers should expose the same `async embed(text: str) -> list[float]` interface. A base class or Protocol in `integrations/` should enforce this before cloud providers are added.

3. **Context window differences**: `nomic-embed-text` supports 8192 tokens. Cloud providers vary. The chunking strategy (ADR-00007) currently ignores provider limits. A provider abstraction should expose a `max_tokens` or `max_chars` property that the indexer can respect.

4. **Re-index on provider switch**: Changing the provider must invalidate the existing ChromaDB collection. The index should record which provider and model it was built with, and warn (or auto-rebuild) on mismatch.
