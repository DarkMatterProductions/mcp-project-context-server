# Continue Dev

## Overview

[Continue](https://www.continue.dev/) is an open-source AI code assistant that works inside both **VS Code** and **JetBrains IDEs**. It supports MCP servers in both **STDIO** (local subprocess) and **HTTP/SSE** (remote server) transport modes. Configuration lives in `~/.continue/config.json` (VS Code default) or `~/.continue/config.yaml`. Continue's config format uses an `experimental.modelContextProtocolServers` key (distinct from the `mcpServers` key used by Claude Desktop and Cursor).

---

## Prerequisites

- Continue extension installed:
  - VS Code: [marketplace.visualstudio.com/items?itemName=Continue.continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue)
  - JetBrains: [plugins.jetbrains.com/plugin/22707-continue](https://plugins.jetbrains.com/plugin/22707-continue)
- Python 3.10+ and `pip`
- For Ollama: [Ollama](https://ollama.com) installed and running
- For SSE/remote: a running team server (see [Team Server topology](../deployment-topologies.md#topology-2-team-server))

---

## Installation

```bash
# Base — for Ollama
pip install mcp-project-context-server

# With Voyage AI
pip install "mcp-project-context-server[voyage]"

# With SSE support (for running a team server)
pip install "mcp-project-context-server[sse]"
```

---

## Configuration

Continue uses its own config format. The MCP server is defined under `experimental.modelContextProtocolServers`.

Config file locations:

| IDE | Default path |
|---|---|
| VS Code | `~/.continue/config.json` |
| JetBrains | `~/.continue/config.json` (shared) |

You can also use `~/.continue/config.yaml` — see YAML examples below.

> **Note:** The `experimental.modelContextProtocolServers` key may move to a stable top-level key in future Continue versions. Check the [Continue MCP documentation](https://docs.continue.dev/customize/context-providers/mcp) for the current schema.

---

### STDIO Example — Ollama (local, JSON config)

**~/.continue/config.json:**
```json
{
  "models": [...],
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "/usr/local/bin/project-context-server",
          "env": {
            "EMBED_PROVIDER": "ollama",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "OLLAMA_EMBED_MODEL": "nomic-embed-text",
            "VECTOR_STORE_PROVIDER": "chroma-local",
            "REPO_PROVIDER": "local"
          }
        }
      }
    ]
  }
}
```

Pull the model:
```bash
ollama pull nomic-embed-text
```

---

### STDIO Example — Ollama (YAML config)

**~/.continue/config.yaml:**
```yaml
models:
  # ... your LLM config here

experimental:
  modelContextProtocolServers:
    - transport:
        type: stdio
        command: /usr/local/bin/project-context-server
        env:
          EMBED_PROVIDER: ollama
          OLLAMA_BASE_URL: "http://localhost:11434"
          OLLAMA_EMBED_MODEL: nomic-embed-text
          VECTOR_STORE_PROVIDER: chroma-local
          REPO_PROVIDER: local
```

---

### STDIO Example — Voyage AI (JSON config)

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "/usr/local/bin/project-context-server",
          "env": {
            "EMBED_PROVIDER": "voyage",
            "VOYAGE_API_KEY": "pa-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "VOYAGE_EMBED_MODEL": "voyage-code-3",
            "VECTOR_STORE_PROVIDER": "chroma-local",
            "REPO_PROVIDER": "local"
          }
        }
      }
    ]
  }
}
```

Get your Voyage API key at [dash.voyageai.com/api-keys](https://dash.voyageai.com/api-keys).

---

### SSE Example — Remote Team Server with Bearer Auth (JSON config)

When connecting to a shared team server running with `MCP_TRANSPORT=sse` and `MCP_AUTH_TYPE=bearer`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "sse",
          "url": "https://mcp.internal.example.com/sse",
          "requestOptions": {
            "headers": {
              "Authorization": "Bearer YOUR_TEAM_MCP_TOKEN"
            }
          }
        }
      }
    ]
  }
}
```

SSE (YAML):
```yaml
experimental:
  modelContextProtocolServers:
    - transport:
        type: sse
        url: "https://mcp.internal.example.com/sse"
        requestOptions:
          headers:
            Authorization: "Bearer YOUR_TEAM_MCP_TOKEN"
```

Obtain `YOUR_TEAM_MCP_TOKEN` from whoever manages your team's MCP server. It corresponds to the `MCP_AUTH_TOKEN` environment variable set on the server.

---

## Embedding Provider Options

| Provider | `EMBED_PROVIDER` | Key variable | Notes |
|---|---|---|---|
| Ollama | `ollama` | `OLLAMA_EMBED_MODEL` | Free, local; great for STDIO mode |
| Voyage AI | `voyage` | `VOYAGE_API_KEY` | Best code retrieval quality |
| OpenAI | `openai` | `OPENAI_API_KEY` | Good general quality |
| Cohere | `cohere` | `COHERE_API_KEY` | Multilingual |
| Google Gemini | `google` | `GOOGLE_API_KEY` | AI Studio key |
| Vertex AI | `google-vertex` | `GOOGLE_CLOUD_PROJECT` | GCP ADC |

For SSE/remote mode, embedding is configured on the server — no client-side env vars needed.

---

## Vector Store Options

### STDIO mode

```json
"env": {
  "VECTOR_STORE_PROVIDER": "chroma-local"
}
```

Or for a shared index:
```json
"env": {
  "VECTOR_STORE_PROVIDER": "pgvector",
  "PGVECTOR_CONNECTION_STRING": "postgresql://user:***@host:5432/dbname"
}
```

### SSE/remote mode

Vector store is configured server-side. No client configuration required.

---

## Repository Provider Options

For local projects, use the default `local` provider and pass the workspace path as `project_path`.

For GitHub repos, add to the `env` block:
```json
"REPO_PROVIDER": "github",
"GITHUB_TOKEN": "ghp_xx...xxxx"
```

---

## Verification / Quick Test

After saving `config.json` (or `config.yaml`):

1. In VS Code: reload the window (`Ctrl+Shift+P` → "Developer: Reload Window")
2. In JetBrains: the extension reloads automatically
3. Open the Continue chat panel
4. Ask:

   > "@project-context Index /path/to/my-project and explain the database layer."

   Or, if Continue has auto-discovered the MCP server:

   > "Use the project-context tool to search for where authentication tokens are validated."

**Troubleshooting:**
- Open Continue's output log in VS Code: **View → Output → Continue**
- Confirm the `command` path is absolute
- For SSE mode: test the server is reachable: `curl -H "Authorization: Bearer *** https://mcp.internal.example.com/health`
- Refer to [Continue's MCP documentation](https://docs.continue.dev/customize/context-providers/mcp) for the current config key names, as they may change between Continue versions
