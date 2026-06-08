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

Install the base package (plus any extras for your chosen embedding provider):

```bash
# Base — works with Ollama (default provider)
pip install mcp-project-context-server

# With Voyage AI embeddings (recommended for quality)
pip install "mcp-project-context-server[voyage]"

# With OpenAI embeddings
pip install "mcp-project-context-server[openai]"

# With pgvector support
pip install "mcp-project-context-server[pgvector]"

# Everything
pip install "mcp-project-context-server[all]"
```

Verify the entry point is available:
```bash
which project-context-server
# e.g. /usr/local/bin/project-context-server  or  ~/.local/bin/project-context-server
```

---

## Configuration

The Claude Desktop config file lives at:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

Open the file (create it if it does not exist) and add a `mcpServers` block. Examples for common configurations follow.

> **Important:** Use the **full absolute path** returned by `which project-context-server`. Claude Desktop does not inherit your shell's `PATH`.

---

### Example 1 — Ollama (fully local, free)

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

Before first use, pull the embedding model:
```bash
ollama pull nomic-embed-text
```

---

### Example 2 — Voyage AI (best code retrieval quality)

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

---

### Example 3 — OpenAI Embeddings

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

Get your OpenAI API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

---

## Embedding Provider Options

| Provider | `EMBED_PROVIDER` value | Key variable | Notes |
|---|---|---|---|
| Ollama (local) | `ollama` | `OLLAMA_EMBED_MODEL` | Free, offline, requires Ollama running |
| Voyage AI | `voyage` | `VOYAGE_API_KEY` | Best code retrieval quality |
| OpenAI | `openai` | `OPENAI_API_KEY` | Good general quality |
| Cohere | `cohere` | `COHERE_API_KEY` | Good multilingual support |
| Google Gemini | `google` | `GOOGLE_API_KEY` | Uses AI Studio key |
| Vertex AI | `google-vertex` | `GOOGLE_CLOUD_PROJECT` | GCP service account / ADC |

See [Configuration Reference](../configuration-reference.md#1-embedding-providers) for all variables.

---

## Vector Store Options

### `chroma-local` (default — recommended for local use)

Data is persisted to `~/.mcp-project-context/chroma` by default. No extra infrastructure needed.

```json
"env": {
  "VECTOR_STORE_PROVIDER": "chroma-local",
  "CHROMA_PERSIST_DIR": "/Users/yourname/.mcp-project-context/chroma"
}
```

### `pgvector` (shared / team use)

Point Claude Desktop at a shared PostgreSQL+pgvector instance:

```json
"env": {
  "VECTOR_STORE_PROVIDER": "pgvector",
  "PGVECTOR_CONNECTION_STRING": "postgresql://mcpuser:password@db.example.com:5432/mcp_context"
}
```

Requires `pip install "mcp-project-context-server[pgvector]"` and `CREATE EXTENSION IF NOT EXISTS vector;` on the PostgreSQL database.

---

## Repository Provider Options

### `local` (default)

Claude Desktop always uses the `local` repo provider. Pass the absolute filesystem path to your project when calling tools:

```
project_path: /Users/yourname/projects/my-app
```

### `github` / `gitlab`

You can point at remote repositories by setting `REPO_PROVIDER=github` and providing a token. This is useful if you want Claude Desktop to pull fresh code directly from GitHub rather than a local clone:

```json
"env": {
  "REPO_PROVIDER": "github",
  "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

Get a GitHub token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope. Then pass `project_path` as `owner/repo` (e.g., `acme/backend`).

---

## Verification / Quick Test

1. **Restart Claude Desktop** after editing `claude_desktop_config.json`
2. Open a new conversation and look for the 🔌 (MCP) icon in the toolbar — `project-context` should be listed
3. In the chat, ask:

   > "Use the project-context MCP server to index `/Users/yourname/projects/my-app` and tell me what it does."

4. Claude will call `index_project_context` and then answer based on the indexed content
5. To confirm the index persisted, start a new conversation and ask a question about the same project — it should answer without re-indexing

**Troubleshooting:**
- If the server does not appear, check `~/Library/Logs/Claude/` (macOS) for error output
- Ensure the `command` path is absolute and the binary is executable (`chmod +x`)
- Ensure Ollama is running if using `EMBED_PROVIDER=ollama`
