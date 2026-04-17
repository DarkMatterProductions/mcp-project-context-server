# MCP Project Context Server

<p align="center">
  <em>A Python MCP server that gives LLMs persistent, searchable access to project context — documentation, architecture decisions, and session notes.</em>
</p>

<div align="center">

[![License](https://img.shields.io/badge/License-AGPL%20v3-purple.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mcp-project-context-server)](https://pypi.org/project/mcp-project-context-server/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-project-context-server)](https://pypi.org/project/mcp-project-context-server/)
[![Version](https://img.shields.io/pypi/v/mcp-project-context-server?label=version)](https://pypi.org/project/mcp-project-context-server/)  
[![Downloads](https://img.shields.io/pypi/dm/mcp-project-context-server)](https://pypi.org/project/mcp-project-context-server/)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)](https://codecov.io/your-org/mcp-project-context-server)
[![Last Commit](https://img.shields.io/github/last-commit/DarkMatterProductions/mcp-project-context-server)]()
[![Issues](https://img.shields.io/github/issues/DarkMatterProductions/mcp-project-context-server)](https://github.com/your-org/mcp-project-context-server/issues)

</div>

---

## 📖 About the Server

**MCP Project Context Server** provides a robust, production-ready Model Context Protocol (MCP) server implementation designed to give Large Language Models (LLMs) persistent, searchable access to your project's contextual information.

### Core Capabilities

- **🔍 Semantic Search Engine**: Query your project documentation using natural language
- **📚 Persistent Knowledge Base**: Store and retrieve information from `.context/` directory structure
- **🏗️ Modular Architecture**: Clean 4-layer design following SOLID principles
- **🎯 ADR Integration**: Full support for Architecture Decision Records with lifecycle management
- **📝 Session Tracking**: Record and retrieve session notes for future reference
- **💾 Vector Store Backend**: ChromaDB for fast, persistent, embedded vector storage
- **🔄 Easy Reindexing**: Rebuild your knowledge base with a single command

### Key Features

- ✅ **Model-Agnostic**: Works with any LLM model via Ollama (Other providers coming)
- ✅ **Configuration-Free**: Environment variable-based setup, no hardcoded paths
- ✅ **Cross-Platform**: POSIX path normalization ensures consistency across OS
- ✅ **Async-First**: All operations use async/await for performance and scalability
- ✅ **Error-Resilient**: Graceful error handling with informative messaging

---

## 🚀 Getting Started

### Prerequisites

Before installing, ensure you have:

- **Python 3.11+** installed
- **Ollama** running with an embedding model (e.g., `nomic-embed-text`)
- At least **2GB RAM** available
- **4.5GB disk space** for ChromaDB (minimum)

### Installation

#### Option 1: PyPI (Recommended)

```bash
pip install mcp-project-context-server
```

#### Option 2: From Source

```bash
git clone https://github.com/your-org/mcp-project-context-server.git
cd mcp-project-context-server
pip install -e ".[dev]"  # Install with development dependencies
```

### Configuration

Set the following environment variables:

```bash
# Ollama Configuration (Required)
export OLLAMA_HOST="http://localhost:11434"
export EMBED_MODEL="nomic-embed-text"

# ChromaDB Configuration (Optional)
export CHROMA_DIR="$HOME/.mcp-data/chroma"

# Runtime Configuration
export EMBED_CONCURRENCY="4"           # Max concurrent embeddings
export PROJECT_PATH="/path/to/project" # Optional, defaults to CWD
```

---

## 🖥️ Client Setup

### Universal MCP Client Integration

The server follows the standard MCP protocol, making it compatible with any MCP client that supports stdio transport.

#### Supported MCP Clients

| Client | Status | Setup Instructions |
|--------|--------|-------------------|
| **Claude Desktop** | ✅ Tested | See [Claude Desktop Setup](#claude-desktop-setup) |
| **Claude Code** | ✅ Tested | See [Claude Code Setup](#claude-code-setup) |
| **Cursor** | ✅ Tested | See [Cursor Setup](#cursor-setup) |
| **Continue** | ✅ Tested | See [Continue Setup](#continue-setup) |
| **Windsurf** | ✅ Compatible | See [Windsurf Setup](#windsurf-setup) |
| **VS Code Copilot** | ✅ Compatible | See [VS Code Copilot Setup](#vs-code-copilot-setup) |

### Claude Desktop Setup

1. **Install the server** (see [Installation](#installation))

2. **Locate the config file** for your OS:

   | OS | Config File Location |
   |----|---------------------|
   | **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
   | **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
   | **Linux** | `~/.config/Claude/claude_desktop_config.json` |

3. **Configure MCP settings** in `claude_desktop_config.json`:

   **Windows:**
   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "OLLAMA_HOST": "http://localhost:11434",
           "EMBED_MODEL": "nomic-embed-text",
           "CHROMA_DIR": "%USERPROFILE%\\.mcp-data\\chroma"
         }
       }
     }
   }
   ```

   **macOS / Linux:**
   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "OLLAMA_HOST": "http://localhost:11434",
           "EMBED_MODEL": "nomic-embed-text",
           "CHROMA_DIR": "~/.mcp-data/chroma"
         }
       }
     }
   }
   ```

3. **Verify the server is connected:**

   ```bash
   claude mcp list
   ```

4. **Use in Claude Code** by referencing the tools directly in your session, or asking questions about your project context.
   - Try asking: *"What was the decision in ADR-00001?"*
   - Verify semantic search works with project-specific queries

### Claude Code Setup

1. **Install the server** (see [Installation](#installation))

2. **Add the MCP server** using one of two methods:

   **Option A — CLI (Recommended):**

   ```bash
   claude mcp add project-context python -- -m mcp_project_context_server
   ```

   To include environment variables:

   ```bash
   claude mcp add project-context \
     -e OLLAMA_HOST=http://localhost:11434 \
     -e EMBED_MODEL=nomic-embed-text \
     -e CHROMA_DIR=~/.mcp-data/chroma \
     -- python -m mcp_project_context_server
   ```

   **Option B — Config file:**

   Claude Code supports both user-level and project-level configuration:

   | Scope | Location |
   |-------|----------|
   | **User (global)** | `~/.claude.json` |
   | **Project** | `.claude/settings.json` (in project root) |

   Add the following to the `mcpServers` key:

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "OLLAMA_HOST": "http://localhost:11434",
           "EMBED_MODEL": "nomic-embed-text",
           "CHROMA_DIR": "~/.mcp-data/chroma"
         }
       }
     }
   }
3. **Verify the server is connected:**

4. **Use in Claude Code** by referencing the tools directly in your session, or asking questions about your project context.

### Cursor Setup

1. **Install the MCP server** (see [Installation](#installation))

2. **Choose a config scope** — Cursor supports both global and project-level MCP configuration:

   | Scope | Windows | macOS / Linux |
   |-------|---------|---------------|
   | **Global** | `%USERPROFILE%\.cursor\mcp.json` | `~/.cursor/mcp.json` |
   | **Project** | `.cursor\mcp.json` (in project root) | `.cursor/mcp.json` (in project root) |

3. **Configure in `mcp.json`**:

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": [
           "-m",
           "mcp_project_context_server"
         ],
         "env": {
           "OLLAMA_HOST": "http://localhost:11434",
           "EMBED_MODEL": "nomic-embed-text",
           "CHROMA_DIR": "~/.mcp-data/chroma"
         }
       }
     }
   }
   ```

4. **Test functionality**:
   - Use `@project-context` in chat
   - Ask context-aware questions about your project
   - Access ADRs and documentation via natural language

### Continue Setup

1. **Install the Continue VS Code or JetBrains extension**

2. **Locate the config file** for your OS:

   | OS | Config File Location |
   |----|---------------------|
   | **Windows** | `%USERPROFILE%\.continue\config.yaml` |
   | **macOS / Linux** | `~/.continue/config.yaml` |

   > Continue also supports `config.json` for legacy setups, but `config.yaml` is the current default.

3. **Add to `config.yaml`**:

   ```yaml
   mcpServers:
     - name: project-context
       command: python
       args:
         - "-m"
         - mcp_project_context_server
       env:
         OLLAMA_HOST: "http://localhost:11434"
         EMBED_MODEL: "nomic-embed-text"
         CHROMA_DIR: "~/.mcp-data/chroma"
   ```

   Or if using `config.json`:

   ```json
   {
     "mcpServers": [
       {
         "name": "project-context",
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "OLLAMA_HOST": "http://localhost:11434",
           "EMBED_MODEL": "nomic-embed-text",
           "CHROMA_DIR": "~/.mcp-data/chroma"
         }
       }
     ]
   }
   ```

4. **Usage**:
   - Trigger context queries in the chat panel
   - Access project documentation mid-conversation
   - Maintain context across multi-turn conversations

### Windsurf Setup

1. **Install MCP server** via terminal or package manager

2. **Locate the MCP config file** for your OS:

   | OS | Config File Location |
   |----|---------------------|
   | **Windows** | `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
   | **macOS / Linux** | `~/.codeium/windsurf/mcp_config.json` |

3. **Configure in `mcp_config.json`** (create if not exists):

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "OLLAMA_HOST": "http://localhost:11434",
           "EMBED_MODEL": "nomic-embed-text",
           "CHROMA_DIR": "~/.mcp-data/chroma"
         }
       }
     }
   }
   ```

4. **Restart Windsurf** and verify the MCP server appears under `Settings → MCP Servers`.

### VS Code Copilot Setup

MCP support is built into VS Code via **GitHub Copilot** (no separate extension required). Requires VS Code 1.99+ with the Copilot extension.

1. **Install the server** (see [Installation](#installation))

2. **Choose a config scope:**

   **Option A — Workspace (`.vscode/mcp.json`):**

   Create `.vscode/mcp.json` in your project root (works identically on all OSes):

   ```json
   {
     "servers": {
       "project-context": {
         "type": "stdio",
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "OLLAMA_HOST": "http://localhost:11434",
           "EMBED_MODEL": "nomic-embed-text",
           "CHROMA_DIR": "${env:USERPROFILE}/.mcp-data/chroma"
         }
       }
     }
   }
   ```

   > **Note:** Use `${env:USERPROFILE}/.mcp-data/chroma` on Windows or `~/.mcp-data/chroma` on macOS/Linux for `CHROMA_DIR`.

   **Option B — User settings (`settings.json`):**

   Open VS Code settings (`Ctrl + ,` / `Cmd + ,`) and add to `settings.json`:

   ```json
   {
     "mcp": {
       "servers": {
         "project-context": {
           "type": "stdio",
           "command": "python",
           "args": ["-m", "mcp_project_context_server"],
           "env": {
             "OLLAMA_HOST": "http://localhost:11434",
             "EMBED_MODEL": "nomic-embed-text",
             "CHROMA_DIR": "~/.mcp-data/chroma"
           }
         }
       }
     }
   }
   ```

3. **Use in Copilot Chat** by switching to **Agent mode** and the MCP tools will be available automatically.

### IDE-Specific Best Practices

#### PyCharm

While PyCharm doesn't natively support MCP, you can:

1. **Use the CLI mode:**

   **Windows (PowerShell):**
   ```powershell
   project-context-server search "your query"
   ```

   **macOS / Linux:**
   ```bash
   project-context-server search "your query"
   ```

2. **Or use the Python interpreter**:
   ```python
   from mcp_project_context_server.server import run
   run()  # Start server, then connect via MCP client
   ```

#### Vim/Neovim (with mcp.nvim)

```lua
-- In your Neovim config (works on Windows, macOS, and Linux)
require('mcp').connect({
  name = 'project-context',
  command = 'python',
  args = {'-m', 'mcp_project_context_server'},
  env = {
    OLLAMA_HOST = 'http://localhost:11434'
  }
})
```

#### Sublime Text (with Sublime MCP)

Similar to VS Code, configure in Sublime's MCP settings file with the same JSON structure.

---

## 🛠️ Usage Examples

### Semantic Search

Ask natural language questions about your project:

```python
# Example: Ask about your project's architecture
# Expected: Retrieves relevant ADRs and documentation

search_project_context(
    query="How do we handle data persistence?",
    n_results=5
)
```

### Load Full Context

Get all documentation at once:

```python
load_project_context()
# Returns concatenated content of:
# - project.md
# - All ADRs
# - Latest session file
```

### Save Session Notes

```python
save_session_summary(
    summary="Investigated chunking strategy alternatives, decided on fixed-size for now"
)
# Creates: .context/sessions/YYYY-MM-DD.md
```

### Rebuild Index

```python
index_project_context()
# Drops existing collection and rebuilds from .context/
```

---

## 📂 Project Structure

```
mcp-project-context-server/
├── src/mcp_project_context_server/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py              # MCP server entry point
│   ├── tools/
│   │   ├── load_context.py    # load_project_context tool
│   │   ├── search_context.py  # search_project_context tool
│   │   ├── save_session.py    # save_session_summary tool
│   │   └── index_context.py   # index_project_context tool
│   ├── integrations/
│   │   ├── chroma/
│   │   │   └── client.py      # ChromaDB client
│   │   └── ollama/
│   │       └── client.py      # Ollama client
│   ├── indexing/
│   │   ├── chroma/
│   │   │   └── indexer.py     # Chunking & embedding pipeline
│   │   └── ollama/
│   │       └── embedder.py    # Embedding wrappers
│   └── helpers/
│       └── context.py         # Utility functions
├── .context/                   # Project context directory
│   ├── project.md             # Project overview
│   ├── sessions/              # Session notes
│   └── decisions/             # ADRs
├── scripts/
│   └── test_client.py         # Integration smoke test
├── README.md
├── pyproject.toml
└── LICENSE
```

---

## 🧪 Testing

### Manual Integration Test

```bash
python scripts/test_client.py
```

### Development Workflow

```bash
# Run pytest
pytest tests/

# Test coverage
pytest --cov=src/mcp_project_context_server

# Lint and format
ruff check src/
black src/
```

---

## 🌐 Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model name |
| `CHROMA_DIR` | `~/.mcp-data/chroma` | ChromaDB persistence directory |
| `EMBED_CONCURRENCY` | `4` | Max concurrent embedding requests |
| `PROJECT_PATH` | CWD | Path to project root (optional) |
| `MCP_TOOL_PREFIX` | `project-context-` | Prefix for tool names |

---

## 🔮 Roadmap

### Planned Features

- [ ] **Auto-reindex**: Watchdog-based file monitoring for automatic reindexing
- [ ] **YAML Configuration**: Replace environment variables with config files
- [ ] **Codebase Indexing**: Repomix integration for source code analysis
- [ ] **Enhanced ADR Tools**: First-class MCP tools for ADR lifecycle
- [ ] **Repository Bootstrapping**: Automatic `.context/` generation
- [ ] **Batch Operations**: Bulk ADR updates and session imports
- [ ] **API Endpoint**: HTTP REST API alternative to MCP tools

### Community Contributions

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📜 Architecture Decision Records

Explore our [ADRs](.context/decisions/) to understand architectural decisions:

- **ADR-00001**: MCP Protocol Selection
- **ADR-00002**: ChromaDB as Vector Store
- **ADR-00003**: Embedding Provider Selection
- **ADR-00004**: Modular Tool Architecture
- **ADR-00005**: Environment Configuration
- **ADR-00006**: Drop & Recreate Indexing
- **ADR-00007**: Chunking Strategy
- **ADR-00008**: POSIX Path Normalization
- **ADR-00009**: Repomix Integration
- **ADR-00010**: ADR Tooling
- **ADR-00011**: Repository Bootstrapping

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

---

## 🙏 Acknowledgments

- **MCP Team**: For the Model Context Protocol
- **ChromaDB**: For the vector store implementation
- **Ollama**: For the embedding model hosting

---

<div align="center">

**Built with ❤️ for better LLM project understanding**

</div>

