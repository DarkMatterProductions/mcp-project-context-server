# ADR-00005: Environment variable configuration with planned YAML layer

## Status
Implemented (environment variables)
Proposed (YAML configuration layer)

## Context

The server requires runtime configuration for five parameters:

- The Ollama server address (`OLLAMA_HOST`)
- The embedding model name (`EMBED_MODEL`)
- The ChromaDB persistence directory (`CHROMA_DIR`)
- The target project path (`PROJECT_PATH`)
- The embedding concurrency limit (`EMBED_CONCURRENCY`)

These values vary between users, machines, and projects. They should not be hardcoded. The following configuration mechanisms were considered:

- **Environment variables**: The standard mechanism for MCP client-server configuration. MCP clients (Claude Code, Continue IDE, etc.) have native support for passing environment variables to server subprocess invocations in their config blocks. No config file parsing required.
- **`.env` files**: Common for local development. Not loaded automatically by MCP client subprocess invocations — would require the server to call `python-dotenv` or equivalent at startup.
- **YAML config file**: Human-readable, supports comments, allows per-project configuration alongside the `.context/` directory. Requires `pyyaml` (already in `requirements.txt`). Needs a defined file location and a precedence rule relative to env vars.
- **Hardcoded defaults only**: Simple but inflexible. Would require code changes for every deployment variation.

MCP client config blocks pass environment variables to the spawned server subprocess. This is the path of least resistance for the primary deployment model.

## Decision

All runtime configuration is provided via environment variables. Defaults are set in the relevant module if no env var is present:

| Variable | Default | Module |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | `integrations/ollama/client.py` |
| `EMBED_MODEL` | `nomic-embed-text` | `integrations/ollama/client.py` |
| `CHROMA_DIR` | `~/.mcp-data/chroma` | `integrations/chroma/client.py` |
| `PROJECT_PATH` | resolved at tool call time | `tools/*.py` |
| `EMBED_CONCURRENCY` | `4` | `indexing/chroma/indexer.py` |

`pyyaml` is already present in `requirements.txt` in anticipation of a YAML configuration layer. See ADR Review Discussion below.

## Consequences

- Users must configure environment variables in their MCP client settings block (e.g., the `env` section of a `mcp-servers.json` or equivalent). There is no config file to edit today.
- There is no central config module — each module reads its own env vars. This is consistent and avoids a global config object, but means there is no single place to audit all configuration.
- `pyyaml` is listed in `requirements.txt` but not in `pyproject.toml`. When the YAML layer is implemented, it must be added to `pyproject.toml` dependencies as well.
- `PROJECT_PATH` is handled differently from the others — it is read at tool call time in individual `tools/` handlers, not at server startup. This allows the same server process to serve multiple project paths if needed in future.

## Alternatives Considered

- **`.env` files**: Rejected as the primary mechanism. MCP client subprocesses do not automatically load `.env` files. Would require the server to add a `python-dotenv` dependency and startup-time file loading.
- **TOML config (pyproject.toml tool section)**: Rejected. `pyproject.toml` is a project metadata file, not a runtime config file. Mixing runtime config with build config creates ambiguity.

## ADR Review Discussion

**YAML configuration layer (Proposed):**

The following design questions must be resolved before implementing the YAML layer:

1. **File location**: Should the config live at `.context/config.yaml` (per-project, alongside the context directory) or `~/.mcp-data/project-context.yaml` (global, user-level)? Per-project config allows different settings per repository but may be committed to VCS accidentally. Global config is safer for secrets but cannot vary by project.

2. **Precedence order**: Should environment variables override YAML values (env vars win), or should YAML set the authoritative config with env vars as an escape hatch? The 12-factor app convention is that env vars win. This is the recommended default.

3. **Scope**: Should YAML config apply to all tools, or can individual projects override only specific keys? A flat key-value YAML file (matching the env var names) is the simplest starting point.

4. **Implementation location**: A `config.py` module in `helpers/` that reads YAML then falls back to env vars would centralize config resolution without changing how individual modules consume values.
