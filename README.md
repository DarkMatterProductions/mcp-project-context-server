# MCP Project Context Server

<p align="center">
  <em>A Python MCP server that gives LLMs persistent, searchable access to project context — documentation, architecture decisions, and session notes.</em>
</p>

<div align="center">

[![Python](https://img.shields.io/pypi/pyversions/mcp-project-context-server)](https://pypi.org/project/mcp-project-context-server/)
[![PyPI](https://img.shields.io/pypi/v/mcp-project-context-server)](https://pypi.org/project/mcp-project-context-server/)
[![License](https://img.shields.io/pypi/l/mcp-project-context-server)](LICENSE)
[![Build](https://img.shields.io/badge/CI-CI-green)](https://github.com/your-org/mcp-project-context-server/actions)

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

- ✅ **Model-Agnostic**: Works with any LLM model via Ollama or other providers
- ✅ **Configuration-Free**: Environment variable-based setup, no hardcoded paths
- ✅ **Cross-Platform**: POSIX path normalization ensures consistency across OS
- ✅ **Async-First**: All operations use async/await for performance and scalability
- ✅ **Error-Resilient**: Graceful error handling with informative messaging
- ✅ **Production-Ready**: Structured for deployment in production environments

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

### Quick Start

```bash
# Start the MCP server
python -m mcp_project_context_server

# Or use the CLI command
project-context-server
```

The server will automatically:
1. Discover or create the `.context/` directory
2. Read existing documentation files
3. Create ChromaDB collections
4. Initialize MCP tool handlers

---

## 🖥️ Client Setup

### Universal MCP Client Integration

The server follows the standard MCP protocol, making it compatible with any MCP client that supports stdio transport.

#### Supported MCP Clients

| Client | Status | Setup Instructions |
|--------|--------|-------------------|
| **Claude Desktop** | ✅ Tested | See [Claude Setup](#claude-desktop-setup) |
| **Cursor** | ✅ Tested | See [Cursor Setup](#cursor-setup) |
| **Continue** | ✅ Tested | See [Continue Setup](#continue-setup) |
| **Windsurf** | ✅ Compatible | See [Windsurf Setup](#windsurf-setup) |
| **VS Code MCP** | ✅ Compatible | See [VS Code MCP Extension](#vs-code-mcp-extension) |

### Claude Desktop Setup

1. **Install the server** (see [Installation](#installation))

2. **Configure MCP settings** in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "project-context": {
      "command": "python",
      "args": ["-m", "mcp_project_context_server"],
      "env": {
        "OLLAMA_HOST": "http://localhost:11434",
        "EMBED_MODEL": "nomic-embed-text",
        "CHROMA_DIR": "/path/to/chroma/data"
      }
    }
  }
}
```

3. **Restart Claude Desktop** and verify the connection:
   - Open a chat
   - Try asking: *"What was the decision in ADR-00001?"*
   - Verify semantic search works with project-specific queries

### Cursor Setup

1. **Install the MCP server** (see [Installation](#installation))

2. **Add to Cursor settings**: Open settings (`Cmd/Ctrl + ,`) → Navigate to MCP section

3. **Configure in `cursor.json`**:

```json
{
  "mcpServers": {
    "project-context": {
      "type": "stdio",
      "command": "python",
      "args": [
        "-m",
        "mcp_project_context_server"
      ],
      "env": {
        "OLLAMA_HOST": "http://localhost:11434",
        "EMBED_MODEL": "nomic-embed-text"
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

1. **Install the Continue VS Code extension**

2. **Add to `settings.json`**:

```json
{
  "mcpServers": {
    "project-context": {
      "command": "python",
      "args": ["-m", "mcp_project_context_server"],
      "env": {
        "OLLAMA_HOST": "http://localhost:11434",
        "EMBED_MODEL": "nomic-embed-text"
      }
    }
  }
}
```

3. **Usage**:
   - Trigger context queries in the chat panel
   - Access project documentation mid-conversation
   - Maintain context across multi-turn conversations

### Windsurf Setup

1. **Install MCP server** via terminal or package manager

2. **Configure in Windsurf settings** (exact path: `Settings → MCP Servers`):

```json
{
  "project-context": {
    "command": "python",
    "args": ["-m", "mcp_project_context_server"],
    "env": {
      "OLLAMA_HOST": "http://localhost:11434"
    }
  }
}
```

### VS Code MCP Extension

1. **Install the "MCP" VS Code extension** from the Marketplace

2. **Configure in `.vscode/mcp.json`** (create if not exists):

```json
{
  "servers": {
    "project-context": {
      "command": "python",
      "args": ["-m", "mcp_project_context_server"],
      "type": "stdio"
    }
  }
}
```

### IDE-Specific Best Practices

#### PyCharm

While PyCharm doesn't natively support MCP, you can:

1. **Use the CLI mode**:
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
-- In your Neovim config
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
