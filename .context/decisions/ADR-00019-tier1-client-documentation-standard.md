# ADR-00019: Tier 1 MCP Client Documentation Standard

**Status:** Accepted
**Date:** 2026-06-08
**Author:** Hermes Agent

## Context

The server supports 9 Tier 1 clients across 3 transport types and multiple
provider combinations (6 embedding providers × 3 vector stores × 4 repository
providers). Without a documentation standard, each client page is written ad hoc
— sections are missing, code examples differ in style, and deployment topology
guidance is scattered or absent. This increases the support burden and raises the
barrier to adoption.

## Decision

Each Tier 1 client receives a dedicated documentation page with the following
seven sections in order:

1. **Overview and transport** — what the client is and which transport it uses.
2. **Prerequisites and install command** — what must be installed before
   configuring the client.
3. **Config file location and format** — the exact file path and a complete,
   copy-paste-ready configuration block with code examples.
4. **Embedding provider options** — how to configure each supported
   `EMBED_PROVIDER` value for this client.
5. **Vector store options** — how to configure each `VECTOR_STORE_PROVIDER`
   value.
6. **Repository provider options** — how to configure each `REPO_PROVIDER`
   value.
7. **Verification step** — a concrete action the user can take to confirm the
   integration is working (e.g., a specific MCP tool call and its expected
   output).

**Tier 1 clients:**

| Transport | Clients |
|-----------|---------|
| STDIO | Claude Desktop, Claude Code, Gemini AI Studio, OpenAI ChatGPT Desktop, Cursor (local), JetBrains AI Assistant + Junie, Continue Dev (local), GitHub Copilot (local) |
| HTTP/SSE | Gemini Enterprise Agent Engine, Cursor (remote), Continue Dev (team), GitHub Copilot (remote) |

Three **deployment topology guides** cover end-to-end setup for the most common
deployment patterns:

- **Local Developer**: single developer, STDIO transport, local Ollama, local
  ChromaDB, local filesystem.
- **Team Server**: shared HTTP/SSE server, bearer auth, shared ChromaDB (HTTP)
  or pgvector, GitHub/GitLab repository provider.
- **Enterprise / Agent Engine**: Google Cloud Run or Agent Engine, google-iam
  auth, pgvector, GitHub repository provider, Voyage or Google embeddings.

## Rationale

- **Consistent seven-section structure**: reduces the cognitive load for new
  users and ensures no critical setup step is omitted regardless of which client
  they are configuring.
- **Copy-paste code examples for each client**: the config file format differs
  significantly between clients (JSON for Claude Desktop, YAML for Continue Dev,
  etc.); explicit per-client examples eliminate ambiguity.
- **Topology guides over a single "getting started" page**: the three topologies
  represent genuinely different infrastructure setups; a single guide would
  either be too abstract or too long. Separate guides let users go directly to
  the topology that matches their deployment.
- **Consistent structure reduces support burden**: support issues are more likely
  to arise from missing or incorrect config than from bugs; a clear, complete
  standard minimises this class of issue.

## Consequences

- Documentation must be updated whenever a new Tier 1 client is added, a new
  provider is introduced, or an environment variable changes name or semantics.
- Topology guides must stay in sync with env var changes (e.g., if a new
  required variable is added, all three topology guides must be updated).
- The seven-section structure is a minimum standard; client pages may include
  additional client-specific sections (e.g., a troubleshooting section for
  clients with known quirks) as long as the seven required sections are present
  and in order.

## Alternatives Considered

- **Single "getting started" page with tabs per client**: reduces maintenance
  surface but makes the page unwieldy as the client count grows; tab-based
  navigation in static site generators is also inconsistently supported. Rejected.
- **Auto-generated documentation from config schema**: reduces manual maintenance
  burden but produces generic reference docs rather than user-friendly setup
  guides with client-specific context. Rejected as a replacement; may be used
  to supplement hand-written guides in the future.
