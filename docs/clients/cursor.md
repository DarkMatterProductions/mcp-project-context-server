# Cursor

## Overview

[Cursor](https://www.cursor.com/) is an AI-powered code editor built on VS Code. It supports MCP servers in two modes: **STDIO** for local single-developer use (the server runs as a subprocess) and **HTTP/SSE** for a shared remote team server. Configuration lives in `.cursor/mcp.json` in the project root or globally at `~/.cursor/mcp.json`.

> **What this server does:** `mcp-project-context-server` indexes and searches the `.context/` directory of a project — `project.md`, ADRs under `.context/decisions/`, and session notes under `.context/sessions/`. It does not index or search your general source code.

---

## Prerequisites

- Cursor installed ([cursor.com](https://www.cursor.com/))
- Python 3.10+ and `pip`
- For Ollama: [Ollama](https://ollama.com) installed and running
- For cloud providers: the relevant API key

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

Cursor reads MCP server config from `.cursor/mcp.json` (project-level, takes precedence) or `~/.cursor/mcp.json` (global).

| Scope | Path | Committed? |
|-------|------|------------|
| **Project** | `.cursor/mcp.json` | Yes — share with your team |
| **Global** | `~/.cursor/mcp.json` | No — personal only |

> **Security note:** If committing `.cursor/mcp.json`, do not hardcode API keys. Omit the key variable from the JSON and set it in your shell profile (`export VOYAGE_API_KEY=...`). Cursor inherits environment variables from the shell that launched it.

> **SSE/remote mode:** If your team runs a shared MCP server, see [HTTP/SSE Examples](#httpssse-examples). Embedding and vector store configuration is done on the server — clients need only the server URL and auth token.

---

## STDIO Embedding Provider Examples

Each example below is a complete `.cursor/mcp.json`. All use `chroma-local` as the vector store (the default). To use a different vector store, see [Vector Store Configuration](#vector-store-configuration).

---

### Ollama (local, free)

No API key required. Requires [Ollama](https://ollama.com) running locally.

```bash
ollama pull nomic-embed-text
```

```json
{
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
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
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
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
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
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
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
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
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
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

Replace the `VECTOR_STORE_PROVIDER` and related variables in any of the examples above.

---

### ChromaDB Local (default)

No extra infrastructure required. Data persists to `~/.mcp-data/chroma` by default.

```json
{
   "env": {
      "VECTOR_STORE_PROVIDER": "chroma-local",
      "CHROMA_DIR": "/home/yourname/.mcp-data/chroma"
   }
}
```

`CHROMA_DIR` is optional — omit it to use the default path.

---

### ChromaDB HTTP

Connects to a remote or containerized ChromaDB instance.

```json
{
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
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

Useful for a shared team index. Requires `pip install "mcp-project-context-server[pgvector]"` and `CREATE EXTENSION IF NOT EXISTS vector;` on the database.

```json
{
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
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

No configuration required — Cursor passes the workspace root as `project_path`. To pin a different path (or make it explicit for a single-project `mcp.json`), set `PROJECT_PATH` in the server's `env` block; it overrides whatever `project_path` value is passed.

---

### GitHub / GitLab / Gitea

> **Current scope:** setting `REPO_PROVIDER` to `github`, `gitlab`, or `gitea` lets every tool operate on a remote repository directly — `list_repositories` discovers repos, and `load_project_context`, `index_project_context`, `search_project_context` read `.context/` content (with `save_session_summary` writing to it) over the provider's REST API whenever `project_path` is an `owner/repo` identifier or a full repository URL. A plain filesystem `project_path` still reads/writes locally, regardless of `REPO_PROVIDER`.

```json
"env": {
  "REPO_PROVIDER": "github",
  "REPO_AUTH_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Get a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope. For GitHub Enterprise Server, also set `"REPO_BASE_URL": "https://github.example.com/api/v3"`.

For GitLab, set `REPO_PROVIDER` to `gitlab` and get a token at **User Settings → Access Tokens** with `read_api` scope (add `"REPO_BASE_URL"` for self-hosted GitLab). For Gitea, set `REPO_PROVIDER` to `gitea`; `REPO_BASE_URL` is required (no default) and a token is available at **Settings → Applications → Manage Access Tokens**.

---

## HTTP/SSE Examples

When your team runs a shared `mcp-project-context-server` instance over HTTP/SSE, configure Cursor to connect to it. Embedding and vector store configuration is done on the server — clients need only the URL and auth token.

### Bearer Auth

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

`YOUR_TEAM_MCP_TOKEN` is the `MCP_AUTH_TOKEN` value set on the server.

> **Security:** Do not commit `.cursor/mcp.json` with a hardcoded bearer token to a public repository.

### No Auth (trusted internal network)

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

1. Open or restart Cursor in your project directory, and make sure it has a `.context/project.md` (create a minimal one if it doesn't yet exist)
2. Open the Cursor Chat panel (`Ctrl+L` / `Cmd+L`)
3. Check that `project-context` appears in the MCP tools list (click the tools icon)
4. Ask:

   > "Index the project context here, then load it and summarize project.md."

5. Cursor Agent will call `index_project_context`, then `load_project_context` or `search_project_context`, and answer grounded in the indexed `.context/` content

**Troubleshooting:**
- Open Cursor's output panel (View → Output → MCP) for server stderr logs
- For STDIO mode: ensure `command` is an absolute path
- For SSE mode: confirm the server is reachable: `curl -H "Authorization: Bearer ..." http://your-server:8080/health`
- Reload the window (`Ctrl+Shift+P` → "Developer: Reload Window") after editing `mcp.json`
