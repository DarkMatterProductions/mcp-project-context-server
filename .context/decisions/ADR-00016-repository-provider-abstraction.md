# ADR-00016: Repository Provider Abstraction

**Status:** Accepted
**Date:** 2026-06-08
**Author:** Hermes Agent

## Context

The server only supported local filesystem access to repositories. For remote
deployments (HTTP/SSE transport, Gemini Agent Engine), the server runs in a
container or cloud environment that does not have the target repositories
checked out locally. Fetching repository content from GitHub, GitLab, or Gitea
via their REST APIs — without requiring a full `git clone` — is necessary to
make the server useful in these deployment topologies.

## Decision

Introduce a `RepositoryProvider` Protocol with the following methods:
`fetch_context_files`, `fetch_source_bundle`, `fetch_source_files`,
`write_file`, `get_default_branch`, `list_repositories`. Four implementations
are provided: `local`, `github`, `gitlab`, `gitea`.

Multi-tenant mode is enabled by `REPO_MULTI_TENANT=true` together with an
allowlist: `APPROVED_ORGS` (comma-separated org names, grants access to all
repos in those orgs) and/or `APPROVED_REPOS` (comma-separated `owner/repo`
pairs). Both can be set simultaneously (union semantics). If multi-tenant mode
is enabled with neither allowlist set, the server fails at startup.

API-first content access: only `.context/` files and `BUNDLE.md` are fetched
per request — not a full clone. Responses are cached with a configurable TTL.

## Rationale

- **API-first over full clone**: lighter for the read-heavy use case; no disk
  space required; faster for large repositories where only a small subset of
  files is needed.
- **httpx for async HTTP**: already a transitive dependency of the MCP stack;
  consistent with the async-first server design.
- **Allowlist-first security model**: in multi-tenant mode, fail at startup if
  no allowlist is configured — prevents accidental exposure of all repositories
  accessible to the API token.
- **`list_repositories` MCP tool**: enables runtime repo discovery by the LLM
  without requiring the operator to hardcode repository paths in client config.
- **GitHub App auth**: supported for GitHub to provide higher rate limits and
  organisation-level access management without per-user token management.

## Consequences

- Gitea requires `REPO_BASE_URL` (no cloud default endpoint); the server fails
  at startup if `REPO_PROVIDER=gitea` and `REPO_BASE_URL` is not set.
- `project_path` now accepts URLs and short `owner/repo` identifiers in addition
  to filesystem paths (see ADR-00008 amendment).
- GitHub App authentication requires additional environment variables
  (`GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`); Personal Access Token
  (`GITHUB_TOKEN`) remains supported as a simpler alternative.
- Content cache TTL must be tuned to balance freshness vs. API rate limits.

## Alternatives Considered

- **Full git clone**: too heavy for a cloud-hosted server; requires persistent
  disk storage proportional to repository count and size; slow for large
  repositories; adds `git` as a runtime dependency. Rejected.
- **Single-repo-per-deployment (Agent Engine model)**: operationally infeasible
  at organisation scale — managing hundreds of separate Agent Engine deployments,
  one per repository, is not maintainable. Rejected in favour of multi-tenant
  support (see also ADR-00018).
