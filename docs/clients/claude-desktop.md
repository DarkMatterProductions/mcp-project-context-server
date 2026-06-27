# Claude Desktop

## Overview

Claude Desktop is Anthropic's native desktop application for macOS and Windows. It supports MCP servers natively via **STDIO transport** — the server runs as a child process of Claude Desktop, and all communication happens over stdin/stdout. No network port or authentication is required.

---

## Prerequisites

- Claude Desktop installed ([download](https://claude.ai/download))
- Python 3.10+ and `pip` available in your `PATH`
- For Ollama: [Ollama](https://ollama.com) installed and running (`ollama serve`)
- For cloud embedding providers: the relevant API key

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

Verify the entry point is available:

```bash
# macOS / Linux
which project-context-server
# e.g. /usr/local/bin/project-context-server  or  ~/.local/bin/project-context-server

# Windows (PowerShell)
(Get-Command project-context-server).Source
# e.g. C:\Users\yourname\AppData\Local\Programs\Python\Python312\Scripts\project-context-server.exe
```

---

## Configuration File Location

| OS | Path |
|----|------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |

Open the file (create it if it does not exist) and add a `mcpServers` block.

> **Important:** Always use the **full absolute path** to `project-context-server`. Claude Desktop does not inherit your shell's `PATH`.

> **Security note:** If any embedding provider requires an API key, avoid hardcoding it in the config file if the file is committed or shared. Set the variable in your shell profile (e.g., `~/.zshrc`) and reference it as `"VOYAGE_API_KEY": "${VOYAGE_API_KEY}"`, or use a secrets manager.

---

## Embedding Provider Examples

Each example below is a complete, working `claude_desktop_config.json`. All use `chroma-local` as the vector store (the default — no extra setup needed). To use a different vector store, see [Vector Store Configuration](#vector-store-configuration).

---

### Ollama (local, free)

No API key required. Requires [Ollama](https://ollama.com) running locally.

```bash
# Pull the embedding model before first use
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

Uses the Google AI Studio API. Suitable for development and personal use. Get an API key at [aistudio.google.com](https://aistudio.google.com/).

```json
{
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
      "env": {
        "EMBED_PROVIDER": "google",
        "GOOGLE_API_KEY": "AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "GOOGLE_EMBED_MODEL": "text-embedding-004",
        "VECTOR_STORE_PROVIDER": "chroma-local",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

> For production workloads with higher quotas and enterprise SLAs, use [Google Vertex AI](#google-vertex-ai) instead.

---

### Google Vertex AI

Uses Application Default Credentials (ADC) — no API key file in the config. Authentication is handled via the Google Cloud SDK.

**Prerequisites:**

1. Enable the Vertex AI API in your [Google Cloud project](https://console.cloud.google.com/apis/library)
2. Authenticate locally:

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
        "VECTOR_STORE_PROVIDER": "chroma-local",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

---

## Vector Store Configuration

The examples above all use `chroma-local` (the default). To switch vector stores, replace the `VECTOR_STORE_PROVIDER` and related variables in any of the examples above.

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

Connects to a remote or containerized ChromaDB instance. No extra pip install required.

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

`CHROMA_API_KEY` is optional — omit it for unauthenticated instances. Replace the `EMBED_PROVIDER` block with your chosen provider.

---

### pgvector (PostgreSQL)

Stores embeddings in PostgreSQL. Requires `pip install "mcp-project-context-server[pgvector]"` and the `pgvector` extension enabled on your database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

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

Replace the `EMBED_PROVIDER` block with your chosen provider.

---

## Repository Provider Configuration

Claude Desktop most commonly uses the `local` provider. Remote providers are available when you want Claude to read from a hosted repository without a local clone.

---

### Local (default)

No configuration required. Pass the absolute path to your project when calling tools:

```
project_path: /Users/yourname/projects/my-app
```

---

### GitHub

```json
"env": {
  "REPO_PROVIDER": "github",
  "REPO_AUTH_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Get a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope (or `public_repo` for public repositories only). Pass `project_path` as `owner/repo` (e.g., `acme/backend`).

For GitHub Enterprise Server, also set:
```json
"REPO_BASE_URL": "https://github.example.com/api/v3"
```

---

### GitLab

```json
"env": {
  "REPO_PROVIDER": "gitlab",
  "REPO_AUTH_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx"
}
```

Get a token at **User Settings → Access Tokens** with `read_api` scope. Pass `project_path` as `namespace/project`.

For self-hosted GitLab, also set:
```json
"REPO_BASE_URL": "https://gitlab.example.com"
```

---

### Gitea

`REPO_BASE_URL` is required — there is no default.

```json
"env": {
  "REPO_PROVIDER": "gitea",
  "REPO_BASE_URL": "https://gitea.example.com",
  "REPO_AUTH_TOKEN": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Get a token at **Settings → Applications → Manage Access Tokens**.

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
| `GOOGLE_EMBED_MODEL` | `google` | `text-embedding-004` | No |
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
| `REPO_AUTH_TOKEN` | `github`, `gitlab`, `gitea` | _(empty)_ | No (required for private repos) |
| `REPO_BASE_URL` | `github`, `gitlab`, `gitea` | _(provider default)_ | **Yes** for `gitea` |
| `REPO_DEFAULT_BRANCH` | `github`, `gitlab`, `gitea` | `main` | No |

---

## Verification / Quick Test

1. **Restart Claude Desktop** after editing `claude_desktop_config.json`
2. Open a new conversation and look for the MCP icon in the toolbar — `project-context` should be listed
3. In the chat, ask:

   > "Use the project-context MCP server to index `/Users/yourname/projects/my-app` and tell me what it does."

4. Claude will call `index_project_context` and then answer based on the indexed content
5. To confirm the index persisted, start a new conversation and ask a question about the same project — it should answer without re-indexing

**Troubleshooting:**

- If the server does not appear, check `~/Library/Logs/Claude/` (macOS) or `%APPDATA%\Claude\logs\` (Windows) for error output
- Ensure the `command` path is absolute and the binary is executable
- Ensure Ollama is running if using `EMBED_PROVIDER=ollama`
- On Windows, use double backslashes (`\\`) in the `command` path or forward slashes
