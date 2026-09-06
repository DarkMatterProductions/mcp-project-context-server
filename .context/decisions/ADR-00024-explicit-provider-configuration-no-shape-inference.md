# ADR-00024: Explicit Provider Configuration — No Inference From Input Shape

## Status
Accepted

## Context
`resolve_project_path()` (`helpers/context.py`) decided whether a `project_path`
argument referred to a remote repository by pattern-matching the raw string —
an `http(s)://` prefix, or a `^[\w.-]+/[\w.-]+$` "owner/repo"-shaped short
identifier — entirely independent of the `REPO_PROVIDER` environment variable
that the rest of the codebase already uses (via `get_repository_provider()`)
to select the active repository provider (`local`, `github`, `gitlab`,
`gitea`).

This meant a `project_path` could be routed down the remote/GitHub code path
purely because it happened to contain exactly one `/`, even when
`REPO_PROVIDER` was unset and defaulted to `local`. The provider selected by
configuration and the code path actually taken at runtime could disagree with
each other, silently and without any error — producing incorrect results
(e.g. indexing 0 chunks) rather than a clear failure.

Every other provider-dependent seam in the codebase (`EMBED_PROVIDER`,
`VECTOR_STORE_PROVIDER`, `REPO_PROVIDER` itself) is resolved by an explicit,
fail-fast, singleton-cached environment variable read once via a `registry.py`
module, never by inspecting the shape of a runtime value to guess intent.
`resolve_project_path()` was the one place that broke this pattern.

## Decision
Provider-dependent behavior must always be driven by an explicit configuration
source — an environment variable (following the existing `*_PROVIDER`
registry pattern) or, where applicable, an explicit command-line/tool
argument — and never inferred by pattern-matching or otherwise guessing from
the shape/content of a data value.

Concretely, `resolve_project_path()` no longer decides "is this remote?" on
its own. It accepts the active provider's name as a parameter and only
applies the URL/short-identifier heuristics when that provider is not
`"local"`. The provider name is always sourced from
`get_repository_provider().provider_name`, i.e. from `REPO_PROVIDER`.

This is not a new mechanism — it is bringing `resolve_project_path()` into
line with the registry pattern already established for `EMBED_PROVIDER` and
`VECTOR_STORE_PROVIDER`.

## Consequences
- Any future function that behaves differently depending on which
  provider/backend is active must accept that selection explicitly (as a
  parameter sourced from a `*_PROVIDER` env var, or an explicit tool
  argument) rather than trying to detect it from input data.
- `project_path` strings that happen to look like `owner/repo` are no longer
  silently treated as remote when `REPO_PROVIDER=local` (the default) — they
  are treated as literal filesystem paths, which will now fail clearly
  (`No .context/ directory found...`) instead of silently misbehaving.
- Code reviewers should treat "detecting X from the shape of a string/value"
  as a specific anti-pattern to flag when X is actually a configuration
  choice, and point back to this ADR.

## Alternatives Considered
- **Keep the heuristic, but make it more precise (tighter regex, stricter URL
  validation):** Rejected — no regex can distinguish "a local directory
  named like `owner/repo`" from an actual remote identifier; the ambiguity is
  fundamental, not a matter of pattern precision.
- **Have `resolve_project_path()` import and call `get_repository_provider()`
  internally:** Rejected in favor of passing `provider_name` in explicitly.
  `helpers/context.py` has no other dependency on `integrations/repository/`
  beyond `normalize_repo_identifier`; keeping `resolve_project_path()` a pure
  function (input in, output out, no hidden global-singleton read) keeps it
  trivially unit-testable and makes the dependency on the active provider
  visible at every call site instead of implicit.
