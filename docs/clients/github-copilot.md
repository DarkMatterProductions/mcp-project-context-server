# GitHub Copilot (VS Code — Agent Mode)

## Overview

[GitHub Copilot](https://github.com/features/copilot) in VS Code supports MCP servers in **agent mode** (Copilot Chat with the "Agent" tab active). It connects via **STDIO** (local subprocess) or **HTTP/SSE** (remote server). Workspace-level configuration lives in `.vscode/mcp.json`; user-level config can be set in VS Code user settings. MCP agent mode requires the GitHub Copilot extension version **1.256 or later**.

---

## Prerequisites

- VS Code with the **GitHub Copilot** extension installed and up to date
- A **GitHub Copilot** subscription (Individual, Business, or Enterprise)
- Agent mode enabled: in VS Code settings, ensure `github.copilot.chat.agent.enabled` is `true` (it is `true` by default in recent versions)
- Python 3.10+ and `pip`
- For Ollama: [Ollama](https://ollama.com) installed and running

---

## Installation

```bash
# Base — for Ollama or any provider
pip install mcp-project-context-server

# With Voyage AI
pip install "mcp-project-context-server[voyage]"

# With OpenAI embeddings
pip install "mcp-project-context-server[openai]"

# With pgvector
pip install "mcp-project-context-server[pgvector]"
```

Verify:
```bash
which project-context-server
```

---

## Configuration

GitHub Copilot reads MCP server config from `.vscode/mcp.json` in the workspace root. This file can be committed to version control so all team members get the same MCP tools.

**Config file locations:**

| Scope | Path | Notes |
|---|---|---|
| Workspace | `.vscode/mcp.json` | Per-project; committed to repo |
| User | VS Code User Settings (`settings.json`) under `mcp` key | Global; not project-specific |

The `.vscode/mcp.json` format:

```json
{
  "servers": {
    "<server-name>": {
      "type": "stdio",
      "command": "<absolute-path-to-binary>",
      "args": [],
      "env": {}
    }
  }
}
```

> **Note:** GitHub Copilot's MCP config uses a `servers` key (not `mcpServers`). The `type` field specifies `"stdio"` or `"sse"`.

---

### STDIO Example — Voyage AI

**.vscode/mcp.json:**
```json
{
  "servers": {
    "project-context": {
      "type": "stdio",
      "command": "/usr/local/bin/project-context-server",
      "args": [],
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

> **Tip:** Instead of hardcoding `VOYAGE_API_KEY`, use VS Code's input variables feature — Copilot will prompt you for the value on first use and store it securely:
> ```json
> "env": {
>   "VOYAGE_API_KEY": "${input:voyageApiKey}"
> }
> ```

---

### STDIO Example — Ollama (fully local)

```json
{
  "servers": {
    "project-context": {
      "type": "stdio",
      "command": "/usr/local/bin/project-context-server",
      "args": [],
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

### SSE Example — Remote Team Server with Bearer Auth

```json
{
  "servers": {
    "project-context": {
      "type": "sse",
      "url": "https://mcp.internal.example.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_TEAM_MCP_TOKEN"
      }
    }
  }
}
```

Obtain `YOUR_TEAM_MCP_TOKEN` from your infrastructure team. It is the `MCP_AUTH_TOKEN` value set on the server.

> **Security:** Do not commit `.vscode/mcp.json` with a hardcoded bearer token to a public repository. Add it to `.gitignore` or use a VS Code input variable instead:
> ```json
> "headers": {
>   "Authorization": "Bearer ${input:mcpToken}"
> }
> ```

---

### SSE Example — No Auth (internal network)

```json
{
  "servers": {
    "project-context": {
      "type": "sse",
      "url": "http://mcp.internal.example.com:8080/sse"
    }
  }
}
```

---

## Embedding Provider Options

| Provider | `EMBED_PROVIDER` | Key variable | Notes |
|---|---|---|---|
| Voyage AI | `voyage` | `VOYAGE_API_KEY` | Best code retrieval quality |
| Ollama | `ollama` | `OLLAMA_EMBED_MODEL` | Free, local |
| OpenAI | `openai` | `OPENAI_API_KEY` | Good general quality |
| Cohere | `cohere` | `COHERE_API_KEY` | Multilingual |
| Google Gemini | `google` | `GOOGLE_API_KEY` | AI Studio key |
| Vertex AI | `google-vertex` | `GOOGLE_CLOUD_PROJECT` | GCP ADC |

For SSE/remote mode, embedding is configured server-side.

---

## Vector Store Options

### STDIO mode

```json
"env": {
  "VECTOR_STORE_PROVIDER": "chroma-local"
}
```

For shared team access:
```json
"env": {
  "VECTOR_STORE_PROVIDER": "pgvector",
  "PGVECTOR_CONNECTION_STRING": "postgresql://user:***@host:5432/dbname"
}
```

Requires: `pip install "mcp-project-context-server[pgvector]"`

### SSE/remote mode

Vector store is configured on the server side.

---

## Repository Provider Options

For local checkouts (most common):
```json
"env": {
  "REPO_PROVIDER": "local"
}
```

For GitHub repos (useful if you want to index without cloning):
```json
"env": {
  "REPO_PROVIDER": "github",
  "GITHUB_TOKEN": "ghp_xx...xxxx"
}
```

Create a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope.

---

## Verification / Quick Test

1. Open your project in VS Code with the `.vscode/mcp.json` in place
2. Open **Copilot Chat** (`Ctrl+Alt+I` / `Cmd+Alt+I`) and switch to the **Agent** tab
3. The `project-context` MCP server should appear in the tools list
4. Ask:

   > "Index this project and give me an overview of the main components."

5. Copilot Agent will call `index_project_context` on the workspace root and then answer

**Troubleshooting:**
- Open the Output panel (View → Output) and select **GitHub Copilot** to see MCP server logs
- If the server doesn't start, verify the `command` path is absolute: open a terminal in VS Code and run `which project-context-server`
- Reload the VS Code window after editing `mcp.json`: `Ctrl+Shift+P` → "Developer: Reload Window"
- For SSE issues: `curl http://your-server:8080/health` to test connectivity
- Check that agent mode is enabled: VS Code Settings → search for `github.copilot.chat.agent.enabled`
