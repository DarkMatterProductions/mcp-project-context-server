# Claude Code

## Overview

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) is Anthropic's agentic CLI tool for software engineering tasks. It supports MCP servers via **STDIO transport** configured through JSON settings files. Claude Code can be configured at a per-project level (`.claude/settings.json`) or globally (`~/.claude/settings.json`).

---

## Prerequisites

- Claude Code installed: `npm install -g @anthropic-ai/claude-code`
- Python 3.10+ and `pip` available in your `PATH`
- For Ollama: [Ollama](https://ollama.com) installed and running
- For cloud providers: the relevant API key

---

## Installation

```bash
# Base — works with Ollama (default)
pip install mcp-project-context-server

# With Voyage AI embeddings
pip install "mcp-project-context-server[voyage]"

# With pgvector support
pip install "mcp-project-context-server[pgvector]"
```

Confirm the entry point:
```bash
which project-context-server
```

---

## Configuration

Claude Code reads MCP server configuration from a `mcp_servers` key in its settings JSON. Place the file in one of these locations:

| Scope | Path | When to use |
|---|---|---|
| Project | `.claude/settings.json` | Per-repository config, committed to version control |
| Global | `~/.claude/settings.json` | Personal config shared across all projects |

> **Tip:** Commit `.claude/settings.json` to your repository so your whole team gets the MCP server automatically when they open the project in Claude Code.

---

### Example 1 — Ollama (fully local)

**.claude/settings.json:**
```json
{
  "mcp_servers": {
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

Pull the embedding model before first use:
```bash
ollama pull nomic-embed-text
```

---

### Example 2 — Voyage AI

**.claude/settings.json:**
```json
{
  "mcp_servers": {
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

> **Security note:** If you commit `.claude/settings.json`, avoid putting API keys directly in the file. Instead, set the environment variable in your shell profile (e.g., `~/.zshrc`) and reference it via `"VOYAGE_API_KEY": "${VOYAGE_API_KEY}"`, or use a secrets manager.

---

## Auto-Injecting `project_path` via CLAUDE.md

Claude Code automatically reads a `CLAUDE.md` file at the root of your repository and injects its contents into every conversation as system context. You can use this to pre-configure the `project_path` so Claude Code always knows which project to index without you having to specify it each time.

**CLAUDE.md:**
```markdown
## MCP Project Context

This project is indexed in the project-context MCP server.
- project_path: /home/user/projects/my-app
- When asked about the codebase, use `search_project_context` with project_path set to the value above.
- To refresh the index after major changes, call `index_project_context` with the same project_path.
```

With this in place, Claude Code will know to pass the correct `project_path` to all project-context tools automatically.

---

## Embedding Provider Options

| Provider | `EMBED_PROVIDER` | Key variable | Notes |
|---|---|---|---|
| Ollama | `ollama` | `OLLAMA_EMBED_MODEL` | Free, local |
| Voyage AI | `voyage` | `VOYAGE_API_KEY` | Best code retrieval quality |
| OpenAI | `openai` | `OPENAI_API_KEY` | Good general quality |
| Cohere | `cohere` | `COHERE_API_KEY` | Multilingual support |
| Google Gemini | `google` | `GOOGLE_API_KEY` | AI Studio key |
| Vertex AI | `google-vertex` | `GOOGLE_CLOUD_PROJECT` | GCP ADC |

---

## Vector Store Options

### `chroma-local` (default)

No extra setup required. Data persists to `~/.mcp-project-context/chroma`.

### `pgvector`

```json
"env": {
  "VECTOR_STORE_PROVIDER": "pgvector",
  "PGVECTOR_CONNECTION_STRING": "postgresql://user:***@host:5432/dbname"
}
```

Useful when your team wants a shared, pre-indexed vector store. Requires `pip install "mcp-project-context-server[pgvector]"`.

---

## Repository Provider Options

Claude Code is almost always used with the `local` repo provider since you work inside a checked-out repository. Set `REPO_PROVIDER=local` (the default) and pass the workspace directory as `project_path`.

To use a remote provider (e.g., for indexing repos you haven't cloned locally):
```json
"env": {
  "REPO_PROVIDER": "github",
  "GITHUB_TOKEN": "ghp_xx...xxxx"
}
```

---

## Verification / Quick Test

Start Claude Code in your project directory:
```bash
cd /path/to/my-project
claude
```

Inside the Claude Code session:
```
> Index this project and summarize its architecture.
```

Claude Code will invoke `index_project_context` on the current directory and then answer. On subsequent runs the index is already built, so queries are fast.

To explicitly trigger a re-index:
```
> Re-index the project context for /path/to/my-project
```
