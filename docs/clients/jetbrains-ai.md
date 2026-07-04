# JetBrains AI Assistant & Junie

## Overview

[JetBrains AI Assistant](https://www.jetbrains.com/ai/) and [Junie](https://www.jetbrains.com/junie/) are AI features built into JetBrains IDEs (IntelliJ IDEA, PyCharm, Rider, WebStorm, GoLand, etc.). Both share the same MCP server configuration, managed through IDE Settings. They connect via **STDIO transport** — the MCP server is launched as a subprocess by the IDE.

**Minimum IDE version required: 2024.2** (earlier versions do not support MCP servers).

> **What this server does:** `mcp-project-context-server` indexes and searches the `.context/` directory of a project — `project.md`, ADRs under `.context/decisions/`, and session notes under `.context/sessions/`. It does not index or search your general source code.

---

## Prerequisites

- JetBrains IDE version **2024.2 or later** with an active [JetBrains AI](https://www.jetbrains.com/ai/) subscription
- AI Assistant plugin enabled (bundled since 2024.1; keep it up to date via **Settings → Plugins**)
- Python 3.10+ and `pip` available in your system `PATH`
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

Verify the entry point:

```bash
# Linux/macOS
which project-context-server
# e.g. /usr/local/bin/project-context-server or ~/.local/bin/project-context-server

# Windows
where.exe project-context-server
# e.g. C:\Users\yourname\AppData\Local\Programs\Python\Python312\Scripts\project-context-server.exe
```

---

## Configuration

MCP servers are configured at: **Settings (`Ctrl+Alt+S`) → Tools → AI Assistant → MCP Servers**

Both **AI Assistant** and **Junie** read from this same configuration. Changes take effect immediately — no IDE restart required.

In the MCP Servers settings panel:
1. Click **+** to add a new server
2. Set **Name**: `project-context`
3. Set **Command**: the full absolute path to `project-context-server`
4. Add environment variables in the **Environment Variables** table

> **Important:** Use the full absolute path for the command. The IDE may not inherit your shell's `PATH` correctly, especially on macOS when launched from Finder.

Each example below shows both the UI table values and the equivalent JSON (for reference — the IDE manages the JSON internally).

---

## Embedding Provider Examples

All examples use `chroma-local` as the vector store (the default). To use a different vector store, see [Vector Store Configuration](#vector-store-configuration).

---

### Ollama (local, free)

```bash
ollama pull nomic-embed-text
```

**Environment variables to enter in the UI:**

| Variable | Value |
|----------|-------|
| `EMBED_PROVIDER` | `ollama` |
| `OLLAMA_HOST` | `http://localhost:11434` |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` |
| `VECTOR_STORE_PROVIDER` | `chroma-local` |
| `REPO_PROVIDER` | `local` |

**JSON equivalent:**

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

| Variable | Value |
|----------|-------|
| `EMBED_PROVIDER` | `voyage` |
| `VOYAGE_API_KEY` | `pa-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `VOYAGE_EMBED_MODEL` | `voyage-code-3` |
| `VECTOR_STORE_PROVIDER` | `chroma-local` |
| `REPO_PROVIDER` | `local` |

**JSON equivalent:**

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

| Variable | Value |
|----------|-------|
| `EMBED_PROVIDER` | `openai` |
| `OPENAI_API_KEY` | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` |
| `VECTOR_STORE_PROVIDER` | `chroma-local` |
| `REPO_PROVIDER` | `local` |

**JSON equivalent:**

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

| Variable | Value |
|----------|-------|
| `EMBED_PROVIDER` | `cohere` |
| `COHERE_API_KEY` | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `COHERE_EMBED_MODEL` | `embed-english-v3.0` |
| `VECTOR_STORE_PROVIDER` | `chroma-local` |
| `REPO_PROVIDER` | `local` |

**JSON equivalent:**

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

| Variable | Value |
|----------|-------|
| `EMBED_PROVIDER` | `google` |
| `GOOGLE_API_KEY` | `AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `GOOGLE_EMBED_MODEL` | `gemini-embedding-2` |
| `VECTOR_STORE_PROVIDER` | `chroma-local` |
| `REPO_PROVIDER` | `local` |

**JSON equivalent:**

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

Uses Application Default Credentials — no API key in the config. Authenticate first:

```bash
gcloud auth application-default login
```

> **Important:** `EMBED_PROVIDER=vertexai` cannot be combined with `chroma-local` or `chroma-http` — the Vertex AI and ChromaDB native dependencies deadlock when loaded into the same process on Windows. Use `VECTOR_STORE_PROVIDER=pgvector` with Vertex AI, as shown below. Requires `pip install "mcp-project-context-server[google-vertex,pgvector]"`.

| Variable | Value |
|----------|-------|
| `EMBED_PROVIDER` | `vertexai` |
| `VERTEXAI_PROJECT` | `my-gcp-project-id` |
| `VERTEXAI_LOCATION` | `us-central1` |
| `VERTEXAI_EMBED_MODEL` | `text-embedding-004` |
| `VECTOR_STORE_PROVIDER` | `pgvector` |
| `PGVECTOR_CONNECTION_STRING` | `postgresql://mcpuser:password@localhost:5432/mcp_context` |
| `REPO_PROVIDER` | `local` |

**JSON equivalent:**

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

| Variable | Value |
|----------|-------|
| `VECTOR_STORE_PROVIDER` | `chroma-local` |
| `CHROMA_DIR` | `/home/yourname/.mcp-data/chroma` _(optional)_ |

---

### ChromaDB HTTP

| Variable | Value |
|----------|-------|
| `VECTOR_STORE_PROVIDER` | `chroma-http` |
| `CHROMA_HOST` | `chroma.example.com` |
| `CHROMA_PORT` | `8000` |
| `CHROMA_API_KEY` | `your-chroma-api-key` _(optional)_ |

---

### pgvector (PostgreSQL)

For shared team indexes. Requires `pip install "mcp-project-context-server[pgvector]"` and `CREATE EXTENSION IF NOT EXISTS vector;` on the database.

| Variable | Value |
|----------|-------|
| `VECTOR_STORE_PROVIDER` | `pgvector` |
| `PGVECTOR_CONNECTION_STRING` | `postgresql://mcpuser:password@db.example.com:5432/mcp_context` |

---

## Repository Provider Configuration

JetBrains IDEs are almost always used with local checkouts, so the default `local` provider is correct.

---

### Local (default)

No configuration required. Pass the project root as `project_path` when invoking tools, or set `PROJECT_PATH` in the environment variables table to pin it — it overrides whatever `project_path` value is passed.

---

### GitHub / GitLab / Gitea

> **Current scope:** setting `REPO_PROVIDER` to `github`, `gitlab`, or `gitea` enables the `list_repositories` tool to discover repositories over the provider's REST API. `load_project_context`, `index_project_context`, `search_project_context`, and `save_session_summary` still read and write `.context/` on the local filesystem, so the repository must be checked out locally and `project_path` must point at that checkout — these tools do not yet fetch `.context/` content remotely.

| Variable | Value |
|----------|-------|
| `REPO_PROVIDER` | `github` |
| `REPO_AUTH_TOKEN` | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

Get a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope. For GitHub Enterprise, also add `REPO_BASE_URL` = `https://github.example.com/api/v3`.

For GitLab, set `REPO_PROVIDER` to `gitlab` and get a token at **User Settings → Access Tokens** with `read_api` scope (add `REPO_BASE_URL` for self-hosted GitLab). For Gitea, set `REPO_PROVIDER` to `gitea`; `REPO_BASE_URL` is required (no default) and a token is available at **Settings → Applications → Manage Access Tokens**.

---

## AI Assistant vs. Junie

Both AI Assistant and Junie share the same MCP server list from **Settings → Tools → AI Assistant → MCP Servers**:

- **AI Assistant**: Inline chat, code completions, and explanations. Can call MCP tools when you explicitly ask ("Search the indexed project context for...").
- **Junie**: Autonomous agent mode. Proactively uses MCP tools as part of multi-step coding tasks. Especially effective with `index_project_context` and `load_project_context` called at the start of a session to pull in `project.md`, ADRs, and prior session notes.

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

1. Open your project in the JetBrains IDE, and make sure it has a `.context/project.md` (create a minimal one if it doesn't yet exist)
2. Open the AI Assistant panel (usually `Alt+\` or **View → Tool Windows → AI Assistant**)
3. Ask:

   > "Use the project-context MCP server to index this project, then load the project context and summarize project.md."

4. AI Assistant will invoke `index_project_context` with the current project root, then `load_project_context` or `search_project_context`, and answer

For Junie:
1. Open the Junie panel (**View → Tool Windows → Junie**)
2. Give it a task:

   > "Index this project's context, then search it for any ADRs about our authentication approach."

**Troubleshooting:**
- If the server doesn't appear, check **Settings → Tools → AI Assistant → MCP Servers** for a red error indicator
- Ensure the IDE version is ≥ 2024.2
- On macOS, open the IDE from a terminal to inherit your shell `PATH` and diagnose startup issues
- Check the IDE log: **Help → Show Log in Finder/Explorer**
