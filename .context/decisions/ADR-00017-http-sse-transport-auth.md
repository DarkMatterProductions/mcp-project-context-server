# ADR-00017: HTTP/SSE Transport and Authentication

**Status:** Accepted
**Date:** 2026-06-08
**Author:** Hermes Agent

## Context

STDIO-only transport prevents deployment as a shared service accessible by
remote clients. Gemini Enterprise Agent Engine requires an HTTP endpoint.
Team Cursor setups and other remote MCP clients also need HTTP access. Running
one local server process per developer is operationally acceptable for
individual use but does not scale to shared team or enterprise deployments.

## Decision

Add HTTP/SSE transport using MCP's `SseServerTransport` backed by Starlette and
served by uvicorn. Transport is selected by the `MCP_TRANSPORT` environment
variable (`stdio` is the default, preserving backward compatibility).

Three authentication types are supported via `MCP_AUTH_TYPE`:

- `none` — no authentication (suitable for localhost or trusted network
  deployments).
- `bearer` — static bearer token. `MCP_AUTH_TOKEN` must be set; the server
  fails at startup if it is not. All requests except `/health` must present the
  token in the `Authorization: Bearer <token>` header.
- `google-iam` — Google Cloud identity tokens. Validates tokens issued by
  Google's IAM service; designed for Agent Engine and Cloud Run deployments
  where the caller is a Google-managed service account.

The `/health` endpoint is always unauthenticated and returns a 200 response,
enabling load-balancer health checks regardless of auth configuration.

## Rationale

- **MCP's `SseServerTransport`**: handles the MCP framing and session lifecycle
  at the protocol layer, keeping the application code free of low-level protocol
  concerns.
- **Starlette middleware for auth**: cleanly separates authentication concerns
  from application logic; middleware can be added or removed without touching
  tool handlers.
- **Google IAM over OAuth 2.0**: Agent Engine callers present short-lived
  identity tokens, not OAuth access tokens. Google IAM validation is the correct
  mechanism; OAuth would require a different token flow and additional
  configuration.
- **`bearer` as the general-purpose option**: covers all remote deployment
  scenarios that do not involve Google Cloud without adding a Google dependency.
- **General-purpose design**: the HTTP/SSE transport is not Agent Engine
  specific — any MCP-compatible HTTP client can use it.

## Consequences

- `starlette`, `uvicorn`, and `httpx` are promoted to core dependencies
  (previously optional or transitive).
- `google-auth` is optional; it is installed via `pip install ...[sse]` for
  deployments requiring `MCP_AUTH_TYPE=google-iam`.
- `MCP_AUTH_TOKEN` must be set when `MCP_AUTH_TYPE=bearer`; the server fails
  fast at startup if it is absent.
- `MCP_TRANSPORT=stdio` deployments are unaffected — no new dependencies are
  imported in STDIO mode.

## Alternatives Considered

- **StreamableHTTP (newer MCP transport)**: less mature client support at the
  time of this decision; fewer MCP clients had implemented it. Remains a viable
  future migration path once client support matures.
- **API gateway auth offload** (e.g., Cloud Endpoints, Kong): valid pattern
  that keeps auth logic out of the application entirely, but adds infrastructure
  complexity and a dependency on the gateway being correctly configured. Rejected
  for the initial implementation in favour of built-in auth that works without
  additional infrastructure.
