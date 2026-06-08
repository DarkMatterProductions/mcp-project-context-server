# Cursor

## Overview

[Cursor](https://www.cursor.com/) is an AI-powered code editor built on VS Code. It supports MCP servers in two modes: **STDIO** for local single-developer use (the server runs as a subprocess) and **HTTP/SSE** for a shared remote team server. Configuration lives in `.cursor/mcp.json` in the project root or globally at `~/.cursor/mcp.json`.

---

## Prerequisites

- Cursor installed ([cursor.com](https://www.cursor.com/))
- Python 3.10+ and `pip`
- For STDIO: local installation of `mcp-project-context-server`
- For SSE/remote: a running team server (see [Team Server topology](../deployment-topologies.md#topology-2-team-server))

---

## Installation

```bash
# Local STDIO use — with Voyage AI (recommended for code quality)
pip install "mcp-project-context-server[voyage]"

# Local STDIO use — with Ollama (free/local)
pip install mcp-project-context-server

# Both SSE client and pgvector (for team server setup)
pip install "mcp-project-context-server[sse,pgvector]"
```

Verify:
```bash
which project-context-server
```

---

## Configuration

Cursor reads MCP server config from `.cursor/mcp.json` (project-level, takes precedence) or `~/.cursor/mcp.json` (global).

| Scope | Path | Committed? |
|---|---|---|
| Project | `.cursor/mcp.json` | Yes — share with your team |
| Global | `~/.cursor/mcp.json` | No — personal only |

---

### STDIO Example — Voyage AI (local, single developer)

**.cursor/mcp.json:**
```json
{
  "mcpServers": {
    "project-context": {
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
}
```

Get your Voyage API key at [dash.voyageai.com/api-keys](https://dash.voyageai.com/api-keys).

> **Tip:** If committing `.cursor/mcp.json`, do not hardcode your API key. Instead, omit `VOYAGE_API_KEY` from the JSON and set it in your shell profile (`export VOYAGE_API_KEY=...`). Cursor inherits environment variables from the shell that launched it.

---

### STDIO Example — Ollama (fully local, no API key)

```json
{
  "mcpServers": {
    "project-context": {
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
}
```

---

### HTTP/SSE Example — Remote Team Server with Bearer Auth

When your team runs a shared `mcp-project-context-server` instance (see [Team Server topology](../deployment-topologies.md#topology-2-team-server)), configure Cursor to connect to it over SSE:

**.cursor/mcp.json:**
```json
{
  "mcpServers": {
    "project-context": {
      "url": "https://mcp.internal.example.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_TEAM_MCP_TOKEN"
      }
    }
  }
}
```

- **`url`**: The SSE endpoint of your running team server. If using the default port: `http://your-server:8080/sse`
- **`Authorization`**: The `MCP_AUTH_TOKEN` value set on the server. Obtain this from your team's infrastructure/ops team.

> **Security note:** The bearer token gives full access to the MCP server. Use a per-developer token if your server supports it, or restrict access by IP. Do not commit this file with the token to a public repository.

---

### HTTP/SSE Example — No Auth (internal network, trusted environment)

```json
{
  "mcpServers": {
    "project-context": {
      "url": "http://mcp.internal.example.com:8080/sse"
    }
  }
}
```

---

## Embedding Provider Options

| Provider | `EMBED_PROVIDER` | Key variable | Notes |
|---|---|---|---|
| Voyage AI | `voyage` | `VOYAGE_API_KEY` | Recommended — best code retrieval |
| Ollama | `ollama` | `OLLAMA_EMBED_MODEL` | Free, local |
| OpenAI | `openai` | `OPENAI_API_KEY` | Good general quality |
| Cohere | `cohere` | `COHERE_API_KEY` | Multilingual |
| Google Gemini | `google` | `GOOGLE_API_KEY` | AI Studio key |
| Vertex AI | `google-vertex` | `GOOGLE_CLOUD_PROJECT` | GCP ADC |

For STDIO mode, set these in the `env` block of `.cursor/mcp.json`. For SSE mode, they are set on the server — clients don't configure embedding providers.

---

## Vector Store Options

### STDIO mode

| Provider | Config | Notes |
|---|---|---|
| `chroma-local` | `"VECTOR_STORE_PROVIDER": "chroma-local"` | Default; persists locally |
| `pgvector` | `"VECTOR_STORE_PROVIDER": "pgvector"` + connection string | Shared with team |

### SSE/remote mode

The vector store is configured entirely on the server side. Team members connecting to a remote server share the same index — no vector store configuration is needed in `.cursor/mcp.json`.

---

## Repository Provider Options

### Local filesystem (STDIO)

The default `local` provider reads from your filesystem. When using Cursor, `project_path` is typically the workspace root:

```
project_path: /home/yourname/projects/my-app
```

### GitHub (for remote repos or team server)

```json
"REPO_PROVIDER": "github",
"GITHUB_TOKEN": "ghp_xx...xxxx"
```

Create a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope.

---

## Verification / Quick Test

1. Open or restart Cursor in your project directory
2. Open the Cursor Chat panel (`Ctrl+L` / `Cmd+L`)
3. Check that `project-context` appears in the MCP tools list (click the 🔌 icon)
4. Ask:

   > "Index this project and tell me what the main entry point does."

5. Cursor Agent will call `index_project_context`, then answer grounded in the actual code

**Troubleshooting:**
- Open Cursor's output panel (View → Output → MCP) for server stderr logs
- For STDIO mode: ensure `command` is an absolute path
- For SSE mode: confirm the server is reachable: `curl -H "Authorization: Bearer ..." http://your-server:8080/health`
- Reload the window (`Ctrl+Shift+P` → "Developer: Reload Window") after editing `mcp.json`
