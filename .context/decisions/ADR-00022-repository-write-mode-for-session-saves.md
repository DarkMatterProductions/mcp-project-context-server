# ADR-00022: Repository Write Mode for Session Saves

**Status:** Accepted
**Date:** 2026-07-05
**Author:** Hermes Agent

## Context

ADR-00016 gave every remote `RepositoryProvider` a `write_file()` method, but
it always wrote to the repository's default branch — there was no way to
target a different branch or create one first. This was fine while
`save_session_summary` only wrote to the local filesystem, but wiring that
tool to write remotely (closing the gap described in ADR-00016 and
ADR-00008's Phase 4 amendment) means every session save from an LLM-driven
tool call would land as a direct, unreviewed commit to `main` (or whatever
branch is configured as default) on someone's GitHub/GitLab/Gitea repository.

That's a meaningfully different risk profile than a local filesystem write:
locally, the file sits in the user's own working tree until they choose to
commit it. Remotely, `write_file()` is itself the commit. Operators running
this server against real team repositories need a choice between "just push
it, I trust the agent" and "put it somewhere I can review before it lands on
the default branch."

Options considered:
- Always write directly to the default branch (or an operator-configured
  branch) — simplest, matches the existing single-branch `write_file()`
  contract, but removes any human review step for remote deployments.
- Always create a new branch per session save — safest by default, but noisy
  (a new branch per `save_session_summary` call, even for trusted
  single-maintainer repos) and requires every `RepositoryProvider`
  implementation to support branch creation.
- Make it configurable per deployment, defaulting to direct writes (matching
  today's `write_file()` behavior for anyone already relying on it) with an
  opt-in branch-per-save mode for teams that want review.

## Decision

`write_file()` on the `RepositoryProvider` Protocol gains an optional
`branch: Optional[str] = None` parameter (`None` = provider's default
branch). A new `create_branch(repo_id, new_branch, from_branch=None)` method
is added to the Protocol so branches can be created ahead of a write.

`save_session_summary` reads `REPO_SESSION_WRITE_MODE` (`"direct"` by
default, or `"branch"`) to choose how it writes to a remote repository:

- **`direct`** (default): writes to `REPO_SESSION_BRANCH` if set, otherwise
  the repository's configured default branch — the same one-branch behavior
  `write_file()` always had.
- **`branch`**: creates a new branch named `mcp-session/{date}-{HHMMSS}` off
  the default branch, writes the session file there, and reports the branch
  name back to the caller so a human can open a PR/MR from it.

`LocalRepositoryProvider` ignores `branch` and treats `create_branch()` as a
no-op — branch semantics don't apply to a plain filesystem write.

Both GitHub's and Gitea's existing-file SHA lookup inside `write_file()` were
missing a `?ref=`/branch-scoped query, so they always read the default
branch's SHA regardless of which branch was actually being written to. This
was latent while there was only ever one target branch; it becomes an active
correctness bug once `branch` can differ from default, so it's fixed as part
of this change.

## Rationale

- **Default to today's behavior**: `direct` mode with no `REPO_SESSION_BRANCH`
  set reproduces the exact behavior `write_file()` already had, so this is
  additive — no existing deployment's behavior changes unless the operator
  opts in.
- **Env-var driven, not per-call**: consistent with every other
  `REPO_*` setting in this server (`REPO_PROVIDER`, `REPO_DEFAULT_BRANCH`,
  `REPO_MULTI_TENANT`, ...) — a deployment-level policy decision, not
  something the LLM caller chooses per tool invocation.
- **`branch` mode names branches deterministically**
  (`mcp-session/{date}-{HHMMSS}`): makes it obvious in the repo's branch list
  which branches came from this server, and avoids collisions between
  same-day saves.

## Consequences

- Operators who want commits to always land directly (today's only
  behavior) don't need to change anything.
- Operators who want a review step before session notes land on a shared
  branch can set `REPO_SESSION_WRITE_MODE=branch`; nothing here automates
  opening a PR/MR — the tool response just reports the branch name so a
  human (or a follow-up agent action) can do so.
- `branch` mode leaves behind one branch per session save; nothing in this
  server deletes or merges them. Operators relying on this mode should expect
  branch cleanup to be a manual or externally-automated step.
- The `?ref=`-scoping fix to GitHub/Gitea's SHA lookup changes behavior only
  when `branch` is explicitly set to something other than the default —
  single-branch (`direct`, unset `REPO_SESSION_BRANCH`) callers see no change.

## Alternatives Considered

- **Always direct-to-default**: rejected as the sole option — no path to
  reviewed writes for teams that want one, and this server explicitly targets
  multi-tenant/team deployments (ADR-00018).
- **Always branch-per-save**: rejected as the default — would surprise
  existing single-maintainer/local-first users with unexpected branch
  proliferation on every session save; kept as an opt-in instead.
- **Per-tool-call `write_mode` argument** (LLM chooses branch vs. direct on
  each call): rejected — inconsistent with how every other repository
  behavior in this server is configured (env vars, not tool arguments), and
  gives the LLM caller a security-relevant choice that should be an operator
  policy instead.
