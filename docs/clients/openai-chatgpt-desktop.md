# OpenAI ChatGPT Desktop

## Overview

[ChatGPT Desktop](https://openai.com/chatgpt/download/) (macOS and Windows) added native MCP support in 2025. It connects to MCP servers via **STDIO transport** — the server is launched as a subprocess and communication happens over stdin/stdout. No network port or authentication setup is required.

> **What this server does:** `mcp-project-context-server` indexes and searches the `.context/` directory of a project — `project.md`, ADRs under `.context/decisions/`, and session notes under `.context/sessions/`. It does not index or search your general source code.

---

## Prerequisites

- ChatGPT Desktop app installed and signed in ([download](https://openai.com/chatgpt/download/))
- ChatGPT Plus, Team, or Enterprise subscription (MCP support requires a paid plan)
- Python 3.10+ and `pip`

---

## Installation

Install the package with the extra that matches your chosen embedding provider:

```bash
# OpenAI (natural pairing with ChatGPT — same API key)
pip install "mcp-project-context-server[openai]"

# Ollama (local, no API key required)
pip install "mcp-project-context-server[ollama]"

# Voyage AI
pip install "mcp-project-context-server[voyage]"

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

Verify the entry point:

```bash
# macOS / Linux
which project-context-server
# e.g. /usr/local/bin/project-context-server

# Windows (PowerShell)
(Get-Command project-context-server).Source
```

---

## Configuration File Location

| OS | Path |
|----|------|
| **macOS** | `~/Library/Application Support/ChatGPT/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\ChatGPT\claude_desktop_config.json` |

> **Note:** The file name `claude_desktop_config.json` reflects shared MCP tooling between Anthropic and OpenAI's desktop apps. Confirm the exact path in ChatGPT Desktop's **Settings → MCP Servers** panel, as it may change across versions.

On macOS, create the directory if it does not exist:

```bash
mkdir -p ~/Library/Application\ Support/ChatGPT/
```

> **Important:** Always use the **full absolute path** to `project-context-server`. ChatGPT Desktop may not inherit your shell's `PATH`.

---

## Embedding Provider Examples

Each example below is a complete `claude_desktop_config.json`. All use `chroma-local` as the vector store (the default). To use a different vector store, see [Vector Store Configuration](#vector-store-configuration).

---

### OpenAI (recommended pairing)

Using `EMBED_PROVIDER=openai` pairs naturally with ChatGPT — both use the same OpenAI API key and infrastructure.

> **About billing:** `OPENAI_API_KEY` is a standard API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys). Embedding calls are billed to your API account separately from your ChatGPT subscription.

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

### Ollama (local, free — no API cost)

No API key required. Requires [Ollama](https://ollama.com) running locally.

```bash
ollama pull nomic-embed-text
```

**macOS / Linux:**

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

**Windows:**

```json
{
  "mcpServers": {
    "project-context": {
      "command": "C:\\Users\\yourname\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\project-context-server.exe",
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
"env": {
  "VECTOR_STORE_PROVIDER": "chroma-local",
  "CHROMA_DIR": "/Users/yourname/.mcp-data/chroma"
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
        "EMBED_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "OPENAI_EMBED_MODEL": "text-embedding-3-small",
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
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
      "env": {
        "EMBED_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "OPENAI_EMBED_MODEL": "text-embedding-3-small",
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

No configuration required. Pass the absolute path to your project as `project_path` when calling tools:

```
project_path: /Users/yourname/projects/my-app
```

Alternatively, set `PROJECT_PATH` in the server's `env` block to pin it — it overrides whatever `project_path` value is passed.

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

1. Save the config file and **restart ChatGPT Desktop**
2. Open a new chat and look for the tools/MCP indicator
3. Make sure `/Users/yourname/projects/my-app/.context/project.md` exists (create a minimal one if it doesn't yet exist)
4. Ask:

   > "Use the project-context server to index `/Users/yourname/projects/my-app`, then load the project context and summarize project.md."

5. ChatGPT will call `index_project_context`, then `load_project_context` or `search_project_context`, and provide an answer grounded in the indexed `.context/` content

**Troubleshooting:**
- If the server does not appear, check ChatGPT Desktop's **Settings → MCP Servers** panel for error messages
- Ensure the `command` path is absolute (`which project-context-server`)
- On Windows, use double backslashes (`\\`) in the `command` path or forward slashes
- Ensure Ollama is running if using `EMBED_PROVIDER=ollama`
