# ADR-00027: Cloud provider support for embeddings

## Status
Superseded by ADR-00014

## Context

This sub-item was originally raised as an open extension inside ADR-00003's ADR Review Discussion — it was never tracked as its own ADR. ADR-00003 chose Ollama as the initial and sole embedding provider, but flagged cloud provider support (OpenAI, Cohere, Google Gemini, etc.) as a planned follow-up, with four open design questions:

1. **Provider selection mechanism**: env var (e.g. `EMBED_PROVIDER=openai`) vs. the (also proposed, also unimplemented — see ADR-00028) YAML config layer.
2. **Common interface**: all providers should expose the same `async embed(text: str) -> list[float]` interface, enforced by a base class or Protocol.
3. **Context window differences**: `nomic-embed-text` supports 8192 tokens; cloud providers vary, and the chunking strategy (ADR-00007) ignored provider limits at the time.
4. **Re-index on provider switch**: switching providers must invalidate the existing vector store collection, since embeddings from different models are not comparable.

## Decision

Resolved by ADR-00014 ("Multi-Provider Embedding Support", Accepted). ADR-00014 introduced an `EmbeddingProvider` Protocol (`provider_name`, `model_name`, `max_chars`, async `embed`) and an `EMBED_PROVIDER`-keyed registry in `integrations/embeddings/registry.py`, with six providers implemented: `ollama`, `voyage`, `openai`, `cohere`, `google`, `google-vertex`. The server fails fast at startup if `EMBED_PROVIDER` is unset or unrecognized, directly answering open question 4 above.

This stub exists only to give the originally-proposed sub-item its own traceable record; see ADR-00014 for the full rationale, consequences, and alternatives.

## Consequences

See ADR-00014.

## Alternatives Considered

See ADR-00014.
