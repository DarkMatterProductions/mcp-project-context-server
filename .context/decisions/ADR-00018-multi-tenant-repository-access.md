# ADR-00018: Multi-Tenant Repository Access

**Status:** Accepted
**Date:** 2026-06-08
**Author:** Hermes Agent

## Context

A separate Agent Engine deployment per repository is operationally
unmanageable at organisation scale. A single server deployment needs to serve
an entire organisation's repositories — potentially hundreds — while maintaining
a clear and auditable access control model. Without a structured multi-tenant
design, the server either exposes all repositories accessible to its API token
(over-broad access) or requires manual per-repo configuration (unscalable).

## Decision

`REPO_MULTI_TENANT=true` enables multi-tenant mode. Access control is governed
by an allowlist with union semantics:

- `APPROVED_ORGS` (comma-separated org names): grants access to all repositories
  in the listed organisations.
- `APPROVED_REPOS` (comma-separated `owner/repo` strings): grants access to
  specific named repositories.
- Both can be set simultaneously; the effective access set is their union.
- If multi-tenant mode is enabled and neither `APPROVED_ORGS` nor
  `APPROVED_REPOS` is set, the server fails at startup.

All `project_path` values are validated against the allowlist before any API
call is made via `validate_repo_access()` — a single centralised enforcement
point. The `list_repositories` MCP tool lets the LLM discover available
repositories at runtime. The LLM maintains the "current repository" in its
context window; there is no server-side per-session state.

## Rationale

- **Allowlist-first**: fail-safe by default — explicit access grant is required
  before any repository is accessible. Prevents accidental over-broad access
  from an unconfigured deployment.
- **Union model** (`APPROVED_ORGS` + `APPROVED_REPOS`): supports mixed grants —
  e.g., all repos in the `acme-corp` org plus a specific `partner/shared-lib`
  repo outside the org.
- **LLM-managed session state**: the server remains stateless between requests;
  the LLM's context window tracks which repository is currently active. Simpler
  server design, leverages the LLM's existing strength at maintaining context.
- **`validate_repo_access()` as single enforcement point**: centralises access
  control logic so that new tools or code paths cannot accidentally bypass it.
- **`list_repositories` MCP tool**: enables dynamic repo discovery without
  requiring operators to enumerate repositories in client configuration files.

## Consequences

- Gitea deployments always require `REPO_BASE_URL` since there is no canonical
  cloud endpoint.
- `list_repositories` is the recommended first call at the start of a
  multi-tenant session; the LLM should call it to understand which repositories
  are available before attempting to load context.
- A single deployment can serve all repositories in a listed organisation (e.g.,
  `DarkMatterProductions`) plus any additional orgs or specific repos added to
  the allowlist.
- Operators must update `APPROVED_ORGS` or `APPROVED_REPOS` and redeploy (or
  restart) to grant access to new repositories; there is no runtime allowlist
  mutation.

## Alternatives Considered

- **Denylist model** (allow all by default, deny specific repos): rejected.
  Fail-open is inappropriate for a service with access to potentially sensitive
  repository content. Allowlist-first is the correct default.
- **Per-request auth tokens** (caller supplies their own GitHub token): adds
  complexity to the MCP client configuration and shifts the access control
  burden to the LLM consumer. Rejected for the initial implementation.
- **Single-repo-per-deployment**: operationally infeasible at org scale — see
  ADR-00016. Rejected.
