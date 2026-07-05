# Continue Dev

## Overview

[Continue](https://www.continue.dev/) is an open-source AI code assistant that works inside both **VS Code** and **JetBrains IDEs**. It supports MCP servers in both **STDIO** (local subprocess) and **HTTP/SSE** (remote server) transport modes. Configuration lives in `~/.continue/config.json` or `~/.continue/config.yaml`. Continue's config format uses an `experimental.modelContextProtocolServers` key (distinct from the `mcpServers` key used by Claude Desktop and Cursor).

> **Note:** The `experimental.modelContextProtocolServers` key may move to a stable top-level key in future Continue versions. Check the [Continue MCP documentation](https://docs.continue.dev/customize/context-providers/mcp) for the current schema.

> **What this server does:** `mcp-project-context-server` indexes and searches the `.context/` directory of a project — `project.md`, ADRs under `.context/decisions/`, and session notes under `.context/sessions/`. It does not index or search your general source code.

---

## Prerequisites

- Continue extension installed:
  - VS Code: [marketplace.visualstudio.com/items?itemName=Continue.continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue)
  - JetBrains: [plugins.jetbrains.com/plugin/22707-continue](https://plugins.jetbrains.com/plugin/22707-continue)
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

---

## Configuration

Config file locations:

| IDE | Default path |
|-----|--------------|
| VS Code | `~/.continue/config.json` (or `config.yaml`) |
| JetBrains | `~/.continue/config.json` (shared) |

The examples below show JSON format. YAML equivalents follow the same structure — see the [Ollama YAML example](#ollama-yaml).

---

## STDIO Embedding Provider Examples

Each example is a complete `~/.continue/config.json`. All use `chroma-local` as the vector store (the default). To use a different vector store, see [Vector Store Configuration](#vector-store-configuration).

> **SSE/remote mode:** For team servers, see [HTTP/SSE Examples](#httpssse-examples). Embedding and vector store configuration is done on the server — clients need only the URL and auth token.

---

### Ollama (local, free)

No API key required. Requires [Ollama](https://ollama.com) running locally.

```bash
ollama pull nomic-embed-text
```

**JSON:**

```json
{
  "models": [],
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
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
    ]
  }
}
```

<a name="ollama-yaml"></a>**YAML:**

```yaml
models: []

experimental:
  modelContextProtocolServers:
    - transport:
        type: stdio
        command: /usr/local/bin/project-context-server
        env:
          EMBED_PROVIDER: ollama
          OLLAMA_HOST: "http://localhost:11434"
          OLLAMA_EMBED_MODEL: nomic-embed-text
          VECTOR_STORE_PROVIDER: chroma-local
          REPO_PROVIDER: local
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
  "models": [],
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
  "models": [],
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
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
    ]
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
  "models": [],
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
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
    ]
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
  "models": [],
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
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
    ]
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
  "models": [],
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
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
    ]
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
  "models": [],
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
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
    ]
  }
}
```

`CHROMA_API_KEY` is optional — omit it for unauthenticated instances.

---

### pgvector (PostgreSQL)

For shared team indexes. Requires `pip install "mcp-project-context-server[pgvector]"` and `CREATE EXTENSION IF NOT EXISTS vector;` on the database.

```json
{
  "models": [],
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
            "VECTOR_STORE_PROVIDER": "pgvector",
            "PGVECTOR_CONNECTION_STRING": "postgresql://mcpuser:password@db.example.com:5432/mcp_context",
            "REPO_PROVIDER": "local"
          }
        }
      }
    ]
  }
}
```

---

## Repository Provider Configuration

---

### Local (default)

No configuration required. Pass the workspace path as `project_path` when invoking tools, or set `PROJECT_PATH` in the server's `env` block to pin it — it overrides whatever `project_path` value is passed.

---

### GitHub / GitLab / Gitea

> **Current scope:** setting `REPO_PROVIDER` to `github`, `gitlab`, or `gitea` lets every tool operate on a remote repository directly — `list_repositories` discovers repos, and `load_project_context`, `index_project_context`, `search_project_context` read `.context/` content (with `save_session_summary` writing to it) over the provider's REST API whenever `project_path` is an `owner/repo` identifier or a full repository URL. A plain filesystem `project_path` still reads/writes locally, regardless of `REPO_PROVIDER`.

Add to the `env` block:

```json
"REPO_PROVIDER": "github",
"REPO_AUTH_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Get a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope. For GitHub Enterprise, also add `"REPO_BASE_URL": "https://github.example.com/api/v3"`.

For GitLab, set `REPO_PROVIDER` to `gitlab` and get a token at **User Settings → Access Tokens** with `read_api` scope (add `"REPO_BASE_URL"` for self-hosted GitLab). For Gitea, set `REPO_PROVIDER` to `gitea`; `REPO_BASE_URL` is required (no default) and a token is available at **Settings → Applications → Manage Access Tokens**.

---

## HTTP/SSE Examples

When connecting to a shared team server running with `MCP_TRANSPORT=sse`:

### Bearer Auth (JSON)

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

**YAML:**

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

`YOUR_TEAM_MCP_TOKEN` corresponds to the `MCP_AUTH_TOKEN` set on the server.

### No Auth (trusted internal network)

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "sse",
          "url": "http://mcp.internal.example.com:8080/sse"
        }
      }
    ]
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

After saving `config.json` (or `config.yaml`), make sure `/path/to/my-project/.context/project.md` exists (create a minimal one if it doesn't yet):

1. In VS Code: reload the window (`Ctrl+Shift+P` → "Developer: Reload Window")
2. In JetBrains: the extension reloads automatically
3. Open the Continue chat panel
4. Ask:

   > "@project-context Index /path/to/my-project, then load the project context and summarize project.md."

**Troubleshooting:**
- Open Continue's output log in VS Code: **View → Output → Continue**
- Confirm the `command` path is absolute
- For SSE mode: test the server is reachable: `curl http://mcp.internal.example.com:8080/health`
- Refer to [Continue's MCP documentation](https://docs.continue.dev/customize/context-providers/mcp) for the current config key names, as they may change between Continue versions
