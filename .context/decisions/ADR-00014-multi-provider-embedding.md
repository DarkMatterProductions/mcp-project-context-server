# ADR-00014: Multi-Provider Embedding Support

**Status:** Accepted
**Date:** 2026-06-08
**Author:** Hermes Agent

## Context

The original design hard-coded Ollama as the sole embedding provider. Teams
using cloud-based LLMs (Claude, Gemini, GPT-4) were forced to also run a local
Ollama server just for embeddings, which is operationally burdensome. Cloud
embedding APIs (Voyage, OpenAI, Cohere, Google) offer higher quality and
eliminate the local dependency for teams that don't need local inference.

The ADR-00003 review discussion had already identified the need for a provider
abstraction with a common interface, a `max_chars`/`max_tokens` property per
provider, and a fail-safe mechanism to prevent silently using the wrong
embeddings after a provider switch.

## Decision

Introduce an `EmbeddingProvider` Protocol (`typing.Protocol`) with four
properties (`provider_name`, `model_name`, `max_chars`) and one async method
(`embed`). A registry keyed by the `EMBED_PROVIDER` environment variable is the
single factory entry point. The server fails fast at startup if `EMBED_PROVIDER`
is not set or contains an unrecognised value. Six providers are implemented:
`ollama`, `voyage`, `openai`, `cohere`, `google`, `google-vertex`.

## Rationale

- **Protocol over ABC**: structural subtyping requires no inheritance; third-party
  providers can satisfy the interface without importing from the server's codebase.
- **Fail-fast registry**: prevents silent use of wrong embeddings — a mismatch
  between indexed and query-time provider produces subtly incorrect results that
  are hard to debug.
- **`max_chars` property**: lets the indexer use provider-appropriate chunk sizes
  instead of a hardcoded constant, automatically accommodating providers with
  different context window sizes.
- **Lazy imports**: provider-specific packages (`voyageai`, `openai`, `cohere`,
  `google-generativeai`, `google-cloud-aiplatform`) are only imported when the
  corresponding provider is selected, keeping the base install lightweight.

## Consequences

- **BREAKING**: `EMBED_PROVIDER` must now be set explicitly in the environment.
  Existing deployments that relied on the implicit Ollama default will fail at
  startup until `EMBED_PROVIDER=ollama` is added to their configuration.
- Chunk sizes now vary per provider (previously hardcoded to 1000 characters).
  Re-indexing after a provider change is mandatory — embeddings from different
  models are not comparable.
- Adding a new provider requires only a new class implementing the Protocol and
  one entry in the registry — no changes to indexing or tool-handler code.
- The `EMBED_MODEL` environment variable continues to work; its interpretation
  is delegated to the selected provider.

## Alternatives Considered

- **Abstract base class (ABC)**: more boilerplate, forces inheritance on every
  implementation, and prevents structural compatibility with external classes.
  Rejected in favour of the lighter Protocol approach.
- **Config file (YAML/TOML)**: more complex to parse and distribute than a
  single env var; not standard for MCP servers. Rejected for initial
  implementation; can be layered on top of the env var mechanism later.
- **Default to Ollama (silent fallback)**: masks misconfiguration — if a team
  deploys the server expecting Voyage embeddings but `EMBED_PROVIDER` is absent,
  the server silently produces Ollama embeddings. Query results degrade without
  any error. Rejected in favour of fail-fast.
