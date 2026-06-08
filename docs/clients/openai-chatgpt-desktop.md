# OpenAI ChatGPT Desktop

## Overview

[ChatGPT Desktop](https://openai.com/chatgpt/download/) (macOS and Windows) added native MCP support in 2025. It connects to MCP servers via **STDIO transport** — the server is launched as a subprocess and communication happens over stdin/stdout. No network port or authentication setup is required.

---

## Prerequisites

- ChatGPT Desktop app installed and signed in ([download](https://openai.com/chatgpt/download/))
- ChatGPT Plus, Team, or Enterprise subscription (MCP support requires a paid plan)
- Python 3.10+ and `pip`
- An OpenAI API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

## Installation

```bash
# With OpenAI embeddings (natural pairing with ChatGPT)
pip install "mcp-project-context-server[openai]"

# Or install all extras for flexibility
pip install "mcp-project-context-server[all]"
```

Verify the entry point is on your `PATH`:
```bash
which project-context-server
# e.g. /usr/local/bin/project-context-server
```

---

## Configuration

ChatGPT Desktop stores MCP server configuration at:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/ChatGPT/claude_desktop_config.json` |
| Windows | `%APPDATA%\ChatGPT\claude_desktop_config.json` |

> **Note:** The file name `claude_desktop_config.json` reflects shared MCP tooling between Anthropic and OpenAI's desktop apps. Confirm the exact path in ChatGPT Desktop's Settings → MCP Servers panel, as it may change across versions.

Open or create the file and add a `mcpServers` block:

---

### Example — OpenAI Embeddings (recommended pairing)

Using `EMBED_PROVIDER=openai` pairs naturally with ChatGPT — both use the same OpenAI API key and infrastructure:

```json
{
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
      "env": {
        "EMBED_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-xxx...xxxx",
        "OPENAI_EMBED_MODEL": "text-embedding-3-small",
        "VECTOR_STORE_PROVIDER": "chroma-local",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

> **About `OPENAI_API_KEY`:** This is a standard API key generated at [platform.openai.com/api-keys](https://platform.openai.com/api-keys). Note that this is your **API key** (billed per token), distinct from your ChatGPT subscription credentials. The embedding calls made by the MCP server are billed to your API account separately from your ChatGPT usage.

For higher retrieval quality at higher cost, use `text-embedding-3-large`:

```json
{
  "mcpServers": {
    "project-context": {
      "command": "/usr/local/bin/project-context-server",
      "env": {
        "EMBED_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-xxx...xxxx",
        "OPENAI_EMBED_MODEL": "text-embedding-3-large",
        "VECTOR_STORE_PROVIDER": "chroma-local",
        "REPO_PROVIDER": "local"
      }
    }
  }
}
```

---

### Example — Ollama (local embeddings, no API cost)

If you want to avoid per-token embedding charges, use Ollama:

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

Install Ollama from [ollama.com](https://ollama.com), then:
```bash
ollama pull nomic-embed-text
```

---

## Embedding Provider Options

| Provider | `EMBED_PROVIDER` | Key variable | Notes |
|---|---|---|---|
| OpenAI | `openai` | `OPENAI_API_KEY` | Natural pairing; `text-embedding-3-small` is cost-effective |
| Ollama | `ollama` | `OLLAMA_EMBED_MODEL` | Free, local, no API cost |
| Voyage AI | `voyage` | `VOYAGE_API_KEY` | Best code-specific retrieval quality |
| Cohere | `cohere` | `COHERE_API_KEY` | Good multilingual support |
| Google Gemini | `google` | `GOOGLE_API_KEY` | Google AI Studio key |
| Vertex AI | `google-vertex` | `GOOGLE_CLOUD_PROJECT` | GCP ADC |

---

## Vector Store Options

### `chroma-local` (default)

Persists to `~/.mcp-project-context/chroma`. No setup required:

```json
"VECTOR_STORE_PROVIDER": "chroma-local"
```

### `pgvector`

For a shared team index:

```json
"VECTOR_STORE_PROVIDER": "pgvector",
"PGVECTOR_CONNECTION_STRING": "postgresql://user:***@host:5432/dbname"
```

Requires: `pip install "mcp-project-context-server[pgvector]"`

---

## Repository Provider Options

For local development, the default `local` provider reads directly from your filesystem. Pass the absolute path to your project as `project_path`:

```
project_path: /Users/yourname/projects/my-app
```

To index GitHub repositories without a local clone:
```json
"REPO_PROVIDER": "github",
"GITHUB_TOKEN": "ghp_xx...xxxx"
```

Create a GitHub token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope.

---

## Verification / Quick Test

1. Save `claude_desktop_config.json` and **restart ChatGPT Desktop**
2. Open a new chat and look for the 🔧 (tools/MCP) indicator
3. Ask:

   > "Use the project-context server to index `/Users/yourname/projects/my-app` and describe its overall structure."

4. ChatGPT will call `index_project_context`, then provide an answer grounded in the actual code

**Troubleshooting:**
- If the server does not appear, check ChatGPT Desktop's Settings → MCP Servers panel for error messages
- Ensure the `command` path is absolute (`which project-context-server`)
- On macOS, `~/Library/Application Support/ChatGPT/` may not exist yet — create it: `mkdir -p ~/Library/Application\ Support/ChatGPT/`
