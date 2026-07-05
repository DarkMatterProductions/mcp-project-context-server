# Claude Code

## Overview

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) is Anthropic's agentic CLI tool for software engineering tasks. It supports MCP servers via **STDIO transport** configured through JSON settings files. Claude Code can be configured at a per-project level (`.claude/settings.json`) or globally (`~/.claude/settings.json`).

> **What this server does:** `mcp-project-context-server` indexes and searches the `.context/` directory of a project — `project.md`, ADRs under `.context/decisions/`, and session notes under `.context/sessions/`. It does not index or search your general source code.

---

## Prerequisites

- Claude Code installed: `npm install -g @anthropic-ai/claude-code`
- Python 3.10+ and `pip` available in your `PATH`
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

Confirm the entry point is available:

```bash
which project-context-server
# e.g. /usr/local/bin/project-context-server  or  ~/.local/bin/project-context-server
```

---

## Configuration

Claude Code reads MCP server configuration from a `mcpServers` key in its settings JSON. Place the file in one of these locations:

| Scope | Path | When to use |
|-------|------|-------------|
| **Project** | `.claude/settings.json` | Per-repository config — commit this so the whole team gets the server automatically |
| **Global** | `~/.claude/settings.json` | Personal config shared across all projects |

> **Tip:** Commit `.claude/settings.json` to your repository so your whole team gets the MCP server automatically when they open the project in Claude Code.

> **Security note:** If any embedding provider requires an API key, avoid committing it to version control. Set the variable in your shell profile (e.g., `~/.zshrc`) and reference it as `"VOYAGE_API_KEY": "${VOYAGE_API_KEY}"`, or use a secrets manager.

---

## Embedding Provider Examples

Each example below is a complete, working `.claude/settings.json`. All use `chroma-local` as the vector store (the default — no extra setup needed). To use a different vector store, see [Vector Store Configuration](#vector-store-configuration).

---

### Ollama (local, free)

No API key required. Requires [Ollama](https://ollama.com) running locally.

```bash
# Pull the embedding model before first use
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

Uses the Google AI Studio API. Suitable for development and personal use. Get an API key at [aistudio.google.com](https://aistudio.google.com/).

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

> For production workloads with higher quotas and enterprise SLAs, use [Google Vertex AI](#google-vertex-ai) instead.

---

### Google Vertex AI

Uses Application Default Credentials (ADC) — no API key in the config. Authentication is handled via the Google Cloud SDK.

> **Important:** `EMBED_PROVIDER=vertexai` cannot be combined with `chroma-local` or `chroma-http` — the Vertex AI and ChromaDB native dependencies deadlock when loaded into the same process on Windows. Use `VECTOR_STORE_PROVIDER=pgvector` with Vertex AI, as shown below.

**Prerequisites:**

1. Enable the Vertex AI API in your [Google Cloud project](https://console.cloud.google.com/apis/library)
2. Authenticate locally:

   ```bash
   gcloud auth application-default login
   ```
3. A PostgreSQL instance with the `pgvector` extension (see [pgvector](#pgvector-postgresql) below), and `pip install "mcp-project-context-server[google-vertex,pgvector]"`

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

The examples above all use `chroma-local` (the default). To switch vector stores, replace the `VECTOR_STORE_PROVIDER` and related variables in any of the examples above.

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

Useful when your team wants a shared, pre-indexed vector store. Requires `pip install "mcp-project-context-server[pgvector]"` and the `pgvector` extension enabled on your database:

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

Claude Code is almost always used with the `local` provider — you are already working inside a checked-out repository. Remote providers are available when you want to index repositories you haven't cloned locally.

---

### Local (default)

No configuration required, but Claude Code does not automatically know your repository root — you (or Claude, once told) must still pass it as `project_path` on each tool call, or pin it as described below.

```json
"env": {
  "REPO_PROVIDER": "local"
}
```

---

### GitHub / GitLab / Gitea

> **Current scope:** setting `REPO_PROVIDER` to `github`, `gitlab`, or `gitea` lets every tool operate on a remote repository directly — `list_repositories` discovers repos, and `load_project_context`, `index_project_context`, `search_project_context` read `.context/` content (with `save_session_summary` writing to it) over the provider's REST API whenever `project_path` is an `owner/repo` identifier or a full repository URL. A plain filesystem `project_path` (which is normal in a Claude Code session, where the repo is already checked out) still reads/writes locally, regardless of `REPO_PROVIDER`.

```json
"env": {
  "REPO_PROVIDER": "github",
  "REPO_AUTH_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Get a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope (or `public_repo` for public repositories only). For GitHub Enterprise Server, also set `"REPO_BASE_URL": "https://github.example.com/api/v3"`.

For GitLab, set `REPO_PROVIDER` to `gitlab` and get a token at **User Settings → Access Tokens** with `read_api` scope (add `"REPO_BASE_URL"` for self-hosted GitLab). For Gitea, set `REPO_PROVIDER` to `gitea`; `REPO_BASE_URL` is required (no default) and a token is available at **Settings → Applications → Manage Access Tokens**.

---

## Pinning `project_path` with `PROJECT_PATH`

Claude Code does not pass the repository root to the server automatically, and `project_path` is a required argument on `load_project_context`, `index_project_context`, `search_project_context`, and `save_session_summary`. For a `.claude/settings.json` dedicated to one repository, set `PROJECT_PATH` in the server's `env` block:

```json
{
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
      "env": {
        "PROJECT_PATH": "/home/user/projects/my-app",
        "EMBED_PROVIDER": "ollama",
        "OLLAMA_HOST": "http://localhost:11434"
      }
    }
  }
}
```

`PROJECT_PATH` overrides whatever `project_path` value the tool call supplies, so Claude does not need to know the absolute path — it can call the tools with any placeholder value for `project_path` and the server will use `PROJECT_PATH` instead.

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

Start Claude Code in your project directory, and make sure it has a `.context/project.md` (create a minimal one if it doesn't yet exist):

```bash
cd /path/to/my-project
claude
```

Inside the Claude Code session:

```
> Index the project context for /path/to/my-project, then load it and summarize project.md.
```

Claude Code will invoke `index_project_context` on the current directory, then `load_project_context` or `search_project_context`, and answer based on the indexed `.context/` content. On subsequent runs the index is already built, so queries are fast.

To explicitly trigger a re-index:

```
> Re-index the project context for /path/to/my-project
```
