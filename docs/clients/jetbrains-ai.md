# JetBrains AI Assistant & Junie

## Overview

[JetBrains AI Assistant](https://www.jetbrains.com/ai/) and [Junie](https://www.jetbrains.com/junie/) are AI features built into JetBrains IDEs (IntelliJ IDEA, PyCharm, Rider, WebStorm, GoLand, etc.). Both share the same MCP server configuration, which is managed through IDE Settings. They connect via **STDIO transport** — the MCP server is launched as a subprocess by the IDE.

**Minimum IDE version required: 2024.2** (earlier versions do not support MCP servers).

---

## Prerequisites

- JetBrains IDE version **2024.2 or later** with an active [JetBrains AI](https://www.jetbrains.com/ai/) subscription
- AI Assistant plugin enabled (bundled since 2024.1; ensure it is up to date via **Settings → Plugins**)
- Python 3.10+ and `pip` available in your system `PATH`
- For Ollama: [Ollama](https://ollama.com) installed and running
- For cloud providers: the relevant API key

---

## Installation

```bash
# Base — works with Ollama (default)
pip install mcp-project-context-server

# With Voyage AI embeddings (recommended for code quality)
pip install "mcp-project-context-server[voyage]"

# With OpenAI embeddings
pip install "mcp-project-context-server[openai]"
```

Verify the entry point:
```bash
which project-context-server
# Linux/macOS: /usr/local/bin/project-context-server or ~/.local/bin/project-context-server
```

On Windows:
```powershell
where.exe project-context-server
# e.g. C:\Users\yourname\AppData\Local\Programs\Python\Python311\Scripts\project-context-server.exe
```

---

## Configuration

MCP servers are configured at: **Settings (Ctrl+Alt+S) → Tools → AI Assistant → MCP Servers**

Both **AI Assistant** (the inline chat/suggestions panel) and **Junie** (the autonomous coding agent panel) read from this same configuration. Changes take effect immediately — no IDE restart required.

In the MCP Servers settings panel:
1. Click **+** to add a new server
2. Set **Name**: `project-context`
3. Set **Command**: the full absolute path to `project-context-server`
4. Add environment variables in the **Environment Variables** table

> **Important:** Use the full absolute path for the command. The IDE may not inherit your shell's `PATH` correctly, especially on macOS when launched from Finder.

---

### Example 1 — Ollama (fully local, free)

In the MCP Servers panel, configure:

| Field | Value |
|---|---|
| Name | `project-context` |
| Command | `/usr/local/bin/project-context-server` |

Environment variables:

| Variable | Value |
|---|---|
| `EMBED_PROVIDER` | `ollama` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` |
| `VECTOR_STORE_PROVIDER` | `chroma-local` |
| `REPO_PROVIDER` | `local` |

The resulting config stored by the IDE (for reference):
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

Pull the Ollama model before first use:
```bash
ollama pull nomic-embed-text
```

---

### Example 2 — Voyage AI (best code retrieval quality)

| Field | Value |
|---|---|
| Name | `project-context` |
| Command | `/usr/local/bin/project-context-server` |

Environment variables:

| Variable | Value |
|---|---|
| `EMBED_PROVIDER` | `voyage` |
| `VOYAGE_API_KEY` | `pa-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `VOYAGE_EMBED_MODEL` | `voyage-code-3` |
| `VECTOR_STORE_PROVIDER` | `chroma-local` |
| `REPO_PROVIDER` | `local` |

Get your Voyage API key at [dash.voyageai.com/api-keys](https://dash.voyageai.com/api-keys).

JSON equivalent:
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

---

## Embedding Provider Options

| Provider | `EMBED_PROVIDER` | Key variable | Notes |
|---|---|---|---|
| Ollama | `ollama` | `OLLAMA_EMBED_MODEL` | Free, local; requires Ollama running |
| Voyage AI | `voyage` | `VOYAGE_API_KEY` | Best code retrieval quality |
| OpenAI | `openai` | `OPENAI_API_KEY` | Good general quality |
| Cohere | `cohere` | `COHERE_API_KEY` | Multilingual support |
| Google Gemini | `google` | `GOOGLE_API_KEY` | AI Studio key |
| Vertex AI | `google-vertex` | `GOOGLE_CLOUD_PROJECT` | GCP ADC |

---

## Vector Store Options

### `chroma-local` (default)

Zero-config persistence to `~/.mcp-project-context/chroma`. Recommended for individual developers.

### `pgvector`

For shared team indexes:

| Variable | Value |
|---|---|
| `VECTOR_STORE_PROVIDER` | `pgvector` |
| `PGVECTOR_CONNECTION_STRING` | `postgresql://user:***@host:5432/dbname` |

Requires: `pip install "mcp-project-context-server[pgvector]"`

---

## Repository Provider Options

JetBrains IDEs are almost always used with local checkouts, so the default `local` provider is correct. Pass the project root as `project_path` when invoking tools.

To use GitHub repos directly:

| Variable | Value |
|---|---|
| `REPO_PROVIDER` | `github` |
| `GITHUB_TOKEN` | `ghp_xx...xxxx` |

Create a token at [github.com/settings/tokens](https://github.com/settings/tokens) with `repo` scope.

---

## AI Assistant vs. Junie

Both AI Assistant and Junie share the same MCP server list from **Settings → Tools → AI Assistant → MCP Servers**:

- **AI Assistant**: Inline chat, code completions, and explanations. Can call MCP tools when you explicitly ask ("Search the project context for...").
- **Junie**: Autonomous agent mode. Proactively uses MCP tools as part of multi-step coding tasks. Especially effective with `index_project_context` called at the start of a session.

---

## Verification / Quick Test

1. Open your project in the JetBrains IDE
2. Open the AI Assistant panel (usually `Alt+\` or **View → Tool Windows → AI Assistant**)
3. Ask:

   > "Use the project-context MCP server to index this project and summarize its architecture."

4. AI Assistant will invoke `index_project_context` with the current project root, then answer

For Junie:
1. Open the Junie panel (**View → Tool Windows → Junie**)
2. Give it a task:

   > "Index this project and then find all places where database connections are created."

**Troubleshooting:**
- If the server doesn't appear, check **Settings → Tools → AI Assistant → MCP Servers** for a red error indicator
- Ensure the IDE version is ≥ 2024.2
- On macOS, open the IDE from a terminal (`/Applications/IntelliJ\ IDEA.app/Contents/MacOS/idea`) to inherit your shell `PATH` and diagnose issues
- Check the IDE log: **Help → Show Log in Finder/Explorer**
