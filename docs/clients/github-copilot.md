# GitHub Copilot (VS Code — Agent Mode)

## Overview

[GitHub Copilot](https://github.com/features/copilot) in VS Code supports MCP servers in **agent mode** (Copilot Chat with the "Agent" tab active). It connects via **STDIO** (local subprocess) or **HTTP/SSE** (remote server). Workspace-level configuration lives in `.vscode/mcp.json`; user-level config can be set in VS Code user settings.

> **Note:** GitHub Copilot's MCP config uses a `servers` key (not `mcpServers`). The `type` field specifies `"stdio"` or `"sse"`. MCP agent mode requires the GitHub Copilot extension version **1.256 or later**.

> **What this server does:** `mcp-project-context-server` indexes and searches the `.context/` directory of a project — `project.md`, ADRs under `.context/decisions/`, and session notes under `.context/sessions/`. It does not index or search your general source code.

---

## Prerequisites

- VS Code with the **GitHub Copilot** extension installed and up to date
- A **GitHub Copilot** subscription (Individual, Business, or Enterprise)
- Agent mode enabled: `github.copilot.chat.agent.enabled` must be `true` (default in recent versions)
- Python 3.10+ and `pip`
- For Ollama: [Ollama](https://ollama.com) installed and running

---

## Installation

Install the package with the extra that matches your chosen embedding provider:

```bash
# Ollama (local, no API key required)
pip install "mcp-project-context-server[ollama]"

# Voyage AI
pip install "mcp-project-context-server[voyage]"

# OpenAI
pip install "mcp-project-context-server[openai]"

# Cohere
pip install "mcp-project-context-server[cohere]"

# Google Gemini (AI Studio)
pip install "mcp-project-context-server[google]"

# Google Vertex AI
pip install "mcp-project-context-server[google-vertex]"

# PostgreSQL vector store (any embedding provider)
pip install "mcp-project-context-server[pgvector]"

# Everything
pip install "mcp-project-context-server[all]"
```

Verify:

```bash
which project-context-server
```

---

## Configuration

**Config file locations:**

| Scope | Path | Notes |
|-------|------|-------|
| **Workspace** | `.vscode/mcp.json` | Per-project; can be committed to repo |
| **User** | VS Code User Settings (`settings.json`) under `mcp` key | Global; not project-specific |

> **Security note:** If committing `.vscode/mcp.json`, use VS Code's input variables feature for API keys so they are not hardcoded:
> ```json
> {
>    "env": {
>       "VOYAGE_API_KEY": "${input:voyageApiKey}"
>    }
> }
> ```
> Copilot will prompt for the value on first use and store it securely.

---

## STDIO Embedding Provider Examples

Each example below is a complete `.vscode/mcp.json`. All use `chroma-local` as the vector store (the default). To use a different vector store, see [Vector Store Configuration](#vector-store-configuration).

> **SSE/remote mode:** For team servers, see [HTTP/SSE Examples](#httpssse-examples).

---

### Ollama (local, free)

No API key required. Requires [Ollama](https://ollama.com) running locally.

```bash
ollama pull nomic-embed-text
```

```json
{
  "servers": {
    "project-context": {
      "type": "stdio",
      "command": "/usr/local/bin/project-context-server",
      "args": [],
      "env": {
        "EMBED_PROVIDER": "ollama",
        "OLLAMA_HOST": "http://localhost:11434",
        "OLLAMA_EMBED_MODEL": "nomic-embed-text",
        "VECTOR_STORE_PROVIDER": "chroma-local",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

**Popular Ollama embedding models:**

| Model | Size | Notes |
|-------|------|-------|
| `nomic-embed-text` | ~274 MB | Fast, good general purpose (default) |
| `mxbai-embed-large` | ~669 MB | Higher quality |
| `all-minilm` | ~46 MB | Lightweight |

---

### Voyage AI

Best retrieval quality for code and technical documentation. Get an API key at [dash.voyageai.com/api-keys](https://dash.voyageai.com/api-keys).

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

**Available models:**

| Model | Notes |
|-------|-------|
| `voyage-code-3` | Code-optimized, default |
| `voyage-3` | General purpose |
| `voyage-3-lite` | Faster, lower cost |

---

### OpenAI

Get an API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

```json
{
  "servers": {
    "project-context": {
      "type": "stdio",
      "command": "/usr/local/bin/project-context-server",
      "args": [],
      "env": {
        "EMBED_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "OPENAI_EMBED_MODEL": "text-embedding-3-small",
        "VECTOR_STORE_PROVIDER": "chroma-local",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

**Available models:**

| Model | Dimensions | Notes |
|-------|-----------|-------|
| `text-embedding-3-small` | 1536 | Fast, cost-effective (default) |
| `text-embedding-3-large` | 3072 | Highest quality |

---

### Cohere

Good multilingual support. Get an API key at [dashboard.cohere.com](https://dashboard.cohere.com/).

```json
{
  "servers": {
    "project-context": {
      "type": "stdio",
      "command": "/usr/local/bin/project-context-server",
      "args": [],
      "env": {
        "EMBED_PROVIDER": "cohere",
        "COHERE_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "COHERE_EMBED_MODEL": "embed-english-v3.0",
        "VECTOR_STORE_PROVIDER": "chroma-local",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

**Available models:**

| Model | Notes |
|-------|-------|
| `embed-english-v3.0` | English, default |
| `embed-multilingual-v3.0` | 100+ languages |

---

### Google Gemini (AI Studio)

Get an API key at [aistudio.google.com](https://aistudio.google.com/).

```json
{
  "servers": {
    "project-context": {
      "type": "stdio",
      "command": "/usr/local/bin/project-context-server",
      "args": [],
      "env": {
        "EMBED_PROVIDER": "google",
        "GOOGLE_API_KEY": "AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "GOOGLE_EMBED_MODEL": "gemini-embedding-2",
        "VECTOR_STORE_PROVIDER": "chroma-local",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

---

### Google Vertex AI

Uses Application Default Credentials — no API key in the config.

> **Important:** `EMBED_PROVIDER=vertexai` cannot be combined with `chroma-local` or `chroma-http` — the Vertex AI and ChromaDB native dependencies deadlock when loaded into the same process on Windows. Use `VECTOR_STORE_PROVIDER=pgvector` with Vertex AI, as shown below. Requires `pip install "mcp-project-context-server[google-vertex,pgvector]"`.

```bash
gcloud auth application-default login
```

```json
{
  "servers": {
    "project-context": {
      "type": "stdio",
      "command": "/usr/local/bin/project-context-server",
      "args": [],
      "env": {
        "EMBED_PROVIDER": "vertexai",
        "VERTEXAI_PROJECT": "my-gcp-project-id",
        "VERTEXAI_LOCATION": "us-central1",
        "VERTEXAI_EMBED_MODEL": "text-embedding-004",
        "VECTOR_STORE_PROVIDER": "pgvector",
        "PGVECTOR_CONNECTION_STRING": "postgresql://mcpuser:password@localhost:5432/mcp_context",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

---

## Vector Store Configuration

Replace the `VECTOR_STORE_PROVIDER` and related variables in the `env` block of any example above.

---

### ChromaDB Local (default)

No extra infrastructure required. Data persists to `~/.mcp-data/chroma` by default.

```json
"env": {
  "VECTOR_STORE_PROVIDER": "chroma-local",
  "CHROMA_DIR": "/home/yourname/.mcp-data/chroma"
}
```

`CHROMA_DIR` is optional — omit it to use the default path.

---

### ChromaDB HTTP

Connects to a remote or containerized ChromaDB instance.

```json
{
  "servers": {
    "project-context": {
      "type": "stdio",
      "command": "/usr/local/bin/project-context-server",
      "args": [],
      "env": {
        "EMBED_PROVIDER": "ollama",
        "OLLAMA_HOST": "http://localhost:11434",
        "OLLAMA_EMBED_MODEL": "nomic-embed-text",
        "VECTOR_STORE_PROVIDER": "chroma-http",
        "CHROMA_HOST": "chroma.example.com",
        "CHROMA_PORT": "8000",
        "CHROMA_API_KEY": "your-chroma-api-key",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

`CHROMA_API_KEY` is optional — omit it for unauthenticated instances.

---

### pgvector (PostgreSQL)

For shared team indexes. Requires `pip install "mcp-project-context-server[pgvector]"` and `CREATE EXTENSION IF NOT EXISTS vector;` on the database.

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
        "VECTOR_STORE_PROVIDER": "pgvector",
        "PGVECTOR_CONNECTION_STRING": "postgresql://mcpuser:password@db.example.com:5432/mcp_context",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

---

## Repository Provider Configuration

---

### Local (default)

No configuration required. The workspace root is used as `project_path`. To pin a different path, set `PROJECT_PATH` in the server's `env` block; it overrides whatever `project_path` value is passed.

---

### GitHub / GitLab / Gitea

> **Current scope:** setting `REPO_PROVIDER` to `github`, `gitlab`, or `gitea` lets every tool operate on a remote repository directly — `list_repositories` discovers repos, and `load_project_context`, `index_project_context`, `search_project_context` read `.context/` content (with `save_session_summary` writing to it) over the provider's REST API whenever `project_path` is an `owner/repo` identifier or a full repository URL. A plain filesystem `project_path` still reads/writes locally, regardless of `REPO_PROVIDER`.

```json
"env": {
  "REPO_PROVIDER": "github",
  "REPO_AUTH_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Get a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope. For GitHub Enterprise, also add `"REPO_BASE_URL": "https://github.example.com/api/v3"`.

For GitLab, set `REPO_PROVIDER` to `gitlab` and get a token at **User Settings → Access Tokens** with `read_api` scope (add `"REPO_BASE_URL"` for self-hosted GitLab). For Gitea, set `REPO_PROVIDER` to `gitea`; `REPO_BASE_URL` is required (no default) and a token is available at **Settings → Applications → Manage Access Tokens**.

---

## HTTP/SSE Examples

When your team runs a shared MCP server over HTTP/SSE, clients connect to it directly — no embedding or vector store configuration needed on the client side.

### Bearer Auth

```json
{
  "servers": {
    "project-context": {
      "type": "sse",
      "url": "https://mcp.internal.example.com/sse",
      "headers": {
        "Authorization": "Bearer ${input:mcpToken}"
      }
    }
  }
}
```

Using `${input:mcpToken}` causes VS Code to prompt for the token securely rather than storing it in the file.

### No Auth (trusted internal network)

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

## Environment Variable Reference

### Embedding Providers

| Variable | Provider | Default | Required |
|----------|----------|---------|----------|
| `EMBED_PROVIDER` | All | — | **Yes** |
| `OLLAMA_HOST` | `ollama` | `http://localhost:11434` | No |
| `OLLAMA_EMBED_MODEL` | `ollama` | `nomic-embed-text` | No |
| `VOYAGE_API_KEY` | `voyage` | — | **Yes** |
| `VOYAGE_EMBED_MODEL` | `voyage` | `voyage-code-3` | No |
| `OPENAI_API_KEY` | `openai` | — | **Yes** |
| `OPENAI_EMBED_MODEL` | `openai` | `text-embedding-3-small` | No |
| `COHERE_API_KEY` | `cohere` | — | **Yes** |
| `COHERE_EMBED_MODEL` | `cohere` | `embed-english-v3.0` | No |
| `GOOGLE_API_KEY` | `google` | — | **Yes** |
| `GOOGLE_EMBED_MODEL` | `google` | `gemini-embedding-2` | No |
| `VERTEXAI_PROJECT` | `vertexai` | — | **Yes** |
| `VERTEXAI_LOCATION` | `vertexai` | — | **Yes** |
| `VERTEXAI_EMBED_MODEL` | `vertexai` | `text-embedding-004` | No |

### Vector Stores

| Variable | Store | Default | Required |
|----------|-------|---------|----------|
| `VECTOR_STORE_PROVIDER` | All | `chroma-local` | No |
| `CHROMA_DIR` | `chroma-local` | `~/.mcp-data/chroma` | No |
| `CHROMA_HOST` | `chroma-http` | `localhost` | No |
| `CHROMA_PORT` | `chroma-http` | `8000` | No |
| `CHROMA_API_KEY` | `chroma-http` | _(none)_ | No |
| `PGVECTOR_CONNECTION_STRING` | `pgvector` | — | **Yes** |

### Repository Providers

| Variable | Provider | Default | Required |
|----------|----------|---------|----------|
| `REPO_PROVIDER` | All | `local` | No |
| `PROJECT_PATH` | All | _(from tool call)_ | No — pins the project root, overriding `project_path` |
| `REPO_AUTH_TOKEN` | `github`, `gitlab`, `gitea` | _(empty)_ | No (required for private repos) |
| `REPO_BASE_URL` | `github`, `gitlab`, `gitea` | _(provider default)_ | **Yes** for `gitea` |
| `REPO_DEFAULT_BRANCH` | `github`, `gitlab`, `gitea` | `main` | No |

---

## Verification / Quick Test

1. Open your project in VS Code with `.vscode/mcp.json` in place, and make sure it has a `.context/project.md` (create a minimal one if it doesn't yet exist)
2. Open **Copilot Chat** (`Ctrl+Alt+I` / `Cmd+Alt+I`) and switch to the **Agent** tab
3. The `project-context` MCP server should appear in the tools list
4. Ask:

   > "Index the project context here, then load it and summarize project.md."

5. Copilot Agent will call `index_project_context` on the workspace root, then `load_project_context` or `search_project_context`, and answer based on the indexed `.context/` content

**Troubleshooting:**
- Open the Output panel (View → Output) and select **GitHub Copilot** to see MCP server logs
- If the server doesn't start, verify the `command` path is absolute
- Reload the VS Code window after editing `mcp.json`: `Ctrl+Shift+P` → "Developer: Reload Window"
- For SSE issues: `curl http://your-server:8080/health` to test connectivity
- Check that agent mode is enabled: VS Code Settings → search for `github.copilot.chat.agent.enabled`
