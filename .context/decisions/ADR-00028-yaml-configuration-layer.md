# ADR-00028: YAML configuration layer

## Status
Proposed

## Context

This sub-item was originally raised as an open extension inside ADR-00005's ADR Review Discussion — it was never tracked as its own ADR. ADR-00005 chose environment variables as the runtime configuration mechanism, but flagged a YAML configuration layer as a planned follow-up, with four open design questions:

1. **File location**: per-project (`.context/config.yaml`, alongside the context directory) vs. global (`~/.mcp-data/project-context.yaml`, user-level). Per-project allows per-repository overrides but risks accidental commits to VCS; global is safer for secrets but cannot vary by project.
2. **Precedence order**: env vars override YAML (12-factor convention, recommended default) vs. YAML as authoritative with env vars as an escape hatch.
3. **Scope**: apply to all tools uniformly, or allow per-project override of individual keys? A flat key-value YAML matching the existing env var names is the simplest starting point.
4. **Implementation location**: a `config.py` module in `helpers/` that reads YAML then falls back to env vars, centralizing resolution without changing how individual modules consume values.

As of this writing, this remains unimplemented: there is no `yaml`/`pyyaml` usage anywhere in `src/`. `pyyaml` sits listed in `requirements.txt` (but not `pyproject.toml`) in anticipation of this feature, per ADR-00005.

## ADR Review Discussion
[Discussion pending — the four questions above are unresolved]

## Decision
[Pending review]

## Consequences

- Would add a config-precedence rule (env vars vs. YAML) that every configurable module must respect, not just the ones that exist today.
- Would require a new centralized resolution module (e.g. `helpers/config.py`) rather than each module reading its own env vars independently, as is done today.
- `pyyaml` would need to move from `requirements.txt` into `pyproject.toml` dependencies.

## Alternatives Considered

- **Environment variables only (status quo)**: this is the current and only configuration mechanism (ADR-00005). Simple, but offers no way to persist or version per-project configuration alongside `.context/`.
- **`.env` files**: rejected in ADR-00005 for the same reason it would apply here — MCP client subprocesses do not automatically load `.env` files, requiring an added `python-dotenv` dependency and startup-time file loading.
