# ADR-00003: Ollama-first embedding provider

## Status
Superseded by ADR-00014

## Context

The server requires an embedding provider to convert text chunks into vector representations for ChromaDB indexing and query similarity search. The options considered were:

- **Ollama (local)**: Runs embedding models locally via the Ollama API. No API key, no cost, no data leaves the machine. Requires Ollama to be running locally with the desired model pulled. The `ollama` Python library provides both sync and async clients.
- **OpenAI Embeddings API**: High-quality embeddings (`text-embedding-3-small`, `text-embedding-3-large`). Requires an API key and sends text data to OpenAI's servers. Per-token cost.
- **Cohere Embed API**: Strong embedding quality, particularly for retrieval tasks. Requires an API key and sends data off-device.
- **Google Gemini Embeddings**: Cloud-based, high quality. Requires a Google API key and sends data off-device.
- **HuggingFace sentence-transformers (local)**: Can run locally without Ollama. Requires a Python ML dependency stack (`torch`, `transformers`, etc.) — significantly heavier than the current dependency footprint.

The original project goal was full local LLM support throughout the stack. Project context files (documentation, ADRs, session notes) may contain sensitive architectural or business information. Keeping embeddings local avoids data leakage, API costs, and internet connectivity requirements.

At the same time, cloud embedding providers offer higher model quality and may be preferred in environments where the data sensitivity concern does not apply.

This decision was superseded on 2026-06-08: Ollama is no longer the default or sole embedding provider. The `EMBED_PROVIDER` environment variable is now required at startup, with supported values `ollama`, `voyage`, `openai`, `cohere`, `google`, `google-vertex` — the server fails fast if it is unset or unrecognised, with no silent fallback. See ADR-00014 for the full multi-provider embedding design.

## Decision

Ollama was chosen as the initial and sole embedding provider. The default model is `nomic-embed-text`, configurable via the `EMBED_MODEL` environment variable. The Ollama host is configurable via `OLLAMA_HOST` (default: `http://localhost:11434`).

The integration is isolated behind `integrations/ollama/` so that the `tools/` and `indexing/` layers have no direct provider dependency. Both sync (`get_embedding`) and async (`get_embedding_async`) interfaces are provided in `integrations/ollama/client.py`. The `indexing/ollama/embedder.py` module provides thin named wrappers (`embed_chunk`, `embed_chunk_async`) for semantic clarity in the indexing pipeline.

Cloud provider support was planned as a configurable extension; the `integrations/` structure was designed to accommodate a provider abstraction. See ADR-00027 for that sub-item's own record and ADR-00014 for its resolution.

## Consequences

- The default setup requires Ollama to be running locally with `nomic-embed-text` pulled (`ollama pull nomic-embed-text`). Without this, `index_project_context` and `search_project_context` will fail.
- The `integrations/` layer must remain provider-agnostic as cloud support is added. Tool handlers and indexing logic must not import from `integrations/ollama/` directly — they must go through `indexing/ollama/embedder.py` or a future abstract interface.
- Switching embedding providers requires re-indexing: embeddings from different models are not comparable. Any `EMBED_MODEL` or provider change should be followed by a call to `index_project_context` to rebuild the collection.

## Alternatives Considered

- **OpenAI / Cohere / Gemini embeddings (cloud only)**: Rejected as the sole option. The local-first goal requires that the server function without internet access or API keys. Cloud providers remain viable as opt-in alternatives once a provider abstraction is introduced.
- **HuggingFace sentence-transformers**: Rejected. While local, the dependency footprint (`torch`, `transformers`, CUDA/CPU build variants) is disproportionate for this server's use case and would significantly complicate installation.
