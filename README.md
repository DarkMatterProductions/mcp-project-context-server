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
[![Issues](https://img.shields.io/github/issues/DarkMatterProductions/mcp-project-context-server)](https://github.com/DarkMatterProductions/mcp-project-context-server/issues)

</div>

---

## 📖 About the Server

**MCP Project Context Server** provides a robust, production-ready Model Context Protocol (MCP) server implementation designed to give Large Language Models (LLMs) persistent, searchable access to your project's contextual information.

### Core Capabilities

- **🔍 Semantic Search Engine**: Query your project documentation using natural language
- **📚 Persistent Knowledge Base**: Store and retrieve information from `.context/` directory structure
- **🏗️ Modular Architecture**: Pluggable embedding providers, vector stores, and repository providers
- **🎯 ADR Integration**: Full support for Architecture Decision Records with lifecycle management
- **📝 Session Tracking**: Record and retrieve session notes for future reference
- **🔄 Easy Reindexing**: Rebuild your knowledge base with a single command

### Key Features

- ✅ **Multi-Provider Embedding**: Ollama, Voyage AI, OpenAI, Cohere, Google Gemini, and Google Vertex AI
- ✅ **Flexible Vector Storage**: ChromaDB (local or HTTP) and pgvector (PostgreSQL)
- ✅ **Multiple Repository Providers**: Local filesystem, GitHub, GitLab, and Gitea
- ✅ **Transport Options**: stdio (default) and HTTP/SSE for remote deployments
- ✅ **Configuration-Free**: Environment variable-based setup, no hardcoded paths
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux
- ✅ **Async-First**: All operations use async/await for performance and scalability
- ✅ **Error-Resilient**: Graceful error handling with informative messaging

---

## 📋 Table of Contents

- [About the Server](#-about-the-server)
- [Prerequisites](#-Prerequisites)
- [Installation](#-installation)
- [Embedding Providers](#-embedding-providers)
  - [Ollama](#ollama)
  - [Voyage AI](#voyage-ai)
  - [OpenAI](#openai)
  - [Cohere](#cohere)
  - [Google Gemini](#google-gemini)
  - [Google Vertex AI](#google-vertex-ai)
- [Vector Stores](#️-vector-stores)
  - [ChromaDB Local (Default)](#chromadb-local-default)
  - [ChromaDB HTTP](#chromadb-http)
  - [pgvector (PostgreSQL)](#pgvector-postgresql)
- [Repository Providers](#-repository-providers)
  - [Local Filesystem (Default)](#local-filesystem-default)
  - [GitHub](#github)
  - [GitLab](#gitlab)
  - [Gitea](#gitea)
  - [Multi-Tenant Mode](#multi-tenant-mode)
- [Transport](#-transport)
  - [stdio (Default)](#stdio-default)
  - [HTTP/SSE](#httpsse)
- [Client Setup](#️-client-setup)
  - [Claude Desktop](#claude-desktop)
  - [Claude Code](#claude-code)
  - [Cursor](#cursor)
  - [Continue](#continue)
  - [Windsurf](#windsurf)
  - [VS Code Copilot](#vs-code-copilot)
- [Tools Reference](#️-tools-reference)
- [Environment Variables Reference](#-environment-variables-reference)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## Prerequisites

Before installing, ensure you have:

- **Python 3.11+** installed
- **Ollama** running with an embedding model (e.g., `nomic-embed-text`)
- At least **2GB RAM** available
- **4.5GB disk space** for ChromaDB (minimum)

## 🚀 Installation

### Core Package

```bash
pip install mcp-project-context-server
```

The core package contains the server, tools, and ChromaDB local integration. It does **not** bundle any embedding provider SDK. You must install the extra for your chosen provider.

### Embedding Provider Extras

Install the extra that matches your chosen embedding provider:

| Provider | Extra | Install Command |
|----------|-------|-----------------|
| Ollama (local, no API key) | `ollama` | `pip install "mcp-project-context-server[ollama]"` |
| Voyage AI | `voyage` | `pip install "mcp-project-context-server[voyage]"` |
| OpenAI | `openai` | `pip install "mcp-project-context-server[openai]"` |
| Cohere | `cohere` | `pip install "mcp-project-context-server[cohere]"` |
| Google Gemini | `google` | `pip install "mcp-project-context-server[google]"` |
| Google Vertex AI | `google-vertex` | `pip install "mcp-project-context-server[google-vertex]"` |

### Vector Store Extras

ChromaDB (local and HTTP) is included in the core package. Install the `pgvector` extra only if you are using PostgreSQL:

```bash
pip install "mcp-project-context-server[pgvector]"
```

### HTTP/SSE Transport Extra

Required only when running the server over HTTP/SSE (remote deployments, Google Agent Engine, etc.):

```bash
pip install "mcp-project-context-server[sse]"
```

### Combining Extras

Multiple extras can be combined in a single install:

```bash
# Ollama with pgvector
pip install "mcp-project-context-server[ollama,pgvector]"

# OpenAI with SSE transport
pip install "mcp-project-context-server[openai,sse]"

# Cohere with pgvector and SSE
pip install "mcp-project-context-server[cohere,pgvector,sse]"
```

### Install Everything

```bash
pip install "mcp-project-context-server[all]"
```

### From Source

```bash
git clone https://github.com/DarkMatterProductions/mcp-project-context-server.git
cd mcp-project-context-server
pip install -e ".[ollama]"  # Replace with your chosen provider extra
```

---

## 🔌 Embedding Providers

The embedding provider is selected by the `EMBED_PROVIDER` environment variable. **This variable is required** — the server will not start without it.

```bash
export EMBED_PROVIDER=ollama  # Replace with your chosen provider
```

Supported values: `ollama`, `voyage`, `openai`, `cohere`, `google`, `vertexai`

---

### Ollama

Ollama runs embedding models locally. No API key is required.

**Install:**

```bash
pip install "mcp-project-context-server[ollama]"
```

**Prerequisites:** [Install Ollama](https://ollama.com/download) and pull an embedding model:

```bash
ollama pull nomic-embed-text
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `ollama` |
| `OLLAMA_HOST` | `http://localhost:11434` | URL of the Ollama server |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=ollama
export OLLAMA_HOST=http://localhost:11434    # Optional — this is the default
export OLLAMA_EMBED_MODEL=nomic-embed-text  # Optional — this is the default
```

**Popular models:**

| Model | Size | Notes |
|-------|------|-------|
| `nomic-embed-text` | ~274 MB | Fast, good general purpose |
| `mxbai-embed-large` | ~669 MB | Higher quality |
| `all-minilm` | ~46 MB | Lightweight, lower quality |

---

### Voyage AI

Voyage AI provides embedding models optimized for code and technical content.

**Install:**

```bash
pip install "mcp-project-context-server[voyage]"
```

**Getting an API Key:**

1. Sign up at [voyageai.com](https://www.voyageai.com/)
2. Navigate to **Dashboard → API Keys**
3. Click **Create new key**, give it a name, and copy the key value

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `voyage` |
| `VOYAGE_API_KEY` | — | **Required.** Your Voyage AI API key |
| `VOYAGE_EMBED_MODEL` | `voyage-code-3` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=voyage
export VOYAGE_API_KEY=pa-...
export VOYAGE_EMBED_MODEL=voyage-code-3  # Optional
```

**Recommended models:**

| Model | Notes |
|-------|-------|
| `voyage-code-3` | Code-optimized, default |
| `voyage-3` | General purpose |
| `voyage-3-lite` | Faster, lower cost |

---

### OpenAI

**Install:**

```bash
pip install "mcp-project-context-server[openai]"
```

**Getting an API Key:**

1. Sign up or log in at [platform.openai.com](https://platform.openai.com/)
2. Navigate to **Dashboard → API Keys**
3. Click **Create new secret key**, give it a name, and copy the key immediately — it is only shown once

> **Billing note:** OpenAI API access is pay-per-use. Add a payment method at [platform.openai.com/account/billing](https://platform.openai.com/account/billing) before your free credits run out.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `openai` |
| `OPENAI_API_KEY` | — | **Required.** Your OpenAI API key |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_EMBED_MODEL=text-embedding-3-small  # Optional
```

**Recommended models:**

| Model | Dimensions | Notes |
|-------|-----------|-------|
| `text-embedding-3-small` | 1536 | Fast, cost-effective, default |
| `text-embedding-3-large` | 3072 | Highest quality |

---

### Cohere

**Install:**

```bash
pip install "mcp-project-context-server[cohere]"
```

**Getting an API Key:**

1. Sign up or log in at [dashboard.cohere.com](https://dashboard.cohere.com/)
2. Navigate to **API Keys** in the left sidebar
3. Click **New Trial Key** (free tier, rate-limited) or **New Production Key**, then copy the value

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `cohere` |
| `COHERE_API_KEY` | — | **Required.** Your Cohere API key |
| `COHERE_EMBED_MODEL` | `embed-english-v3.0` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=cohere
export COHERE_API_KEY=...
export COHERE_EMBED_MODEL=embed-english-v3.0  # Optional
```

**Recommended models:**

| Model | Notes |
|-------|-------|
| `embed-english-v3.0` | English, default |
| `embed-multilingual-v3.0` | 100+ languages |

---

### Google Gemini

Uses the Google AI Studio API (Gemini embedding models).

**Install:**

```bash
pip install "mcp-project-context-server[google]"
```

**Getting an API Key:**

1. Sign in at [aistudio.google.com](https://aistudio.google.com/)
2. Click **Get API key** in the top navigation
3. Click **Create API key** — choose an existing Google Cloud project or create a new one
4. Copy the generated key

> **Note:** Google AI Studio keys are suitable for development and personal use. For production workloads with higher quotas and enterprise SLAs, use [Google Vertex AI](#google-vertex-ai) instead.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `google` |
| `GOOGLE_API_KEY` | — | **Required.** Your Google AI Studio API key |
| `GOOGLE_EMBED_MODEL` | `text-embedding-004` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=google
export GOOGLE_API_KEY=AIza...
export GOOGLE_EMBED_MODEL=text-embedding-004  # Optional
```

---

### Google Vertex AI

Uses the Vertex AI SDK with Google Cloud Application Default Credentials (ADC). No API key is required — authentication is handled through your Google Cloud identity.

**Install:**

```bash
pip install "mcp-project-context-server[google-vertex]"
```

**Prerequisites:**

1. **Enable the Vertex AI API** in your Google Cloud project:
   - Open [console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library)
   - Search for **Vertex AI API** and click **Enable**

2. **Authenticate** using Application Default Credentials. For local development:

   ```bash
   gcloud auth application-default login
   ```

   For production environments (e.g. Cloud Run, GKE), assign a service account with the **Vertex AI User** role (`roles/aiplatform.user`) to your workload, and set `GOOGLE_APPLICATION_CREDENTIALS` if using a key file.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `vertexai` |
| `VERTEXAI_PROJECT` | — | **Required.** Your Google Cloud project ID |
| `VERTEXAI_LOCATION` | — | **Required.** Google Cloud region (e.g. `us-central1`) |
| `VERTEXAI_EMBED_MODEL` | `text-embedding-004` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=vertexai
export VERTEXAI_PROJECT=my-gcp-project-id
export VERTEXAI_LOCATION=us-central1
export VERTEXAI_EMBED_MODEL=text-embedding-004  # Optional
```

---

## 🗄️ Vector Stores

The vector store is selected by the `VECTOR_STORE_PROVIDER` environment variable. Defaults to `chroma-local`.

Supported values: `chroma-local`, `chroma-http`, `pgvector`

---

### ChromaDB Local (Default)

Persists embeddings in a local directory. Included in the core package — no extra installation required.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_STORE_PROVIDER` | `chroma-local` | Set to `chroma-local` or omit |
| `CHROMA_DIR` | `~/.mcp-data/chroma` | Directory where ChromaDB stores its data |

**Example:**

```bash
export VECTOR_STORE_PROVIDER=chroma-local  # Optional — this is the default
export CHROMA_DIR=~/.mcp-data/chroma       # Optional — this is the default
```

---

### ChromaDB HTTP

Connects to a remote or containerized ChromaDB instance over HTTP.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_STORE_PROVIDER` | `chroma-local` | Must be set to `chroma-http` |
| `CHROMA_HOST` | `localhost` | ChromaDB server hostname |
| `CHROMA_PORT` | `8000` | ChromaDB server port |
| `CHROMA_API_KEY` | _(none)_ | API key for ChromaDB Cloud or authenticated instances |

**Example:**

```bash
export VECTOR_STORE_PROVIDER=chroma-http
export CHROMA_HOST=chroma.example.com
export CHROMA_PORT=8000
export CHROMA_API_KEY=your-chroma-api-key  # Optional
```

---

### pgvector (PostgreSQL)

Stores embeddings in a PostgreSQL database using the `pgvector` extension.

**Install:**

```bash
pip install "mcp-project-context-server[pgvector]"
```

**Prerequisites:** A PostgreSQL instance (13+) with the `pgvector` extension enabled:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_STORE_PROVIDER` | `chroma-local` | Must be set to `pgvector` |
| `PGVECTOR_CONNECTION_STRING` | — | **Required.** PostgreSQL connection string |

**Example:**

```bash
export VECTOR_STORE_PROVIDER=pgvector
export PGVECTOR_CONNECTION_STRING=postgresql://user:password@localhost:5432/mydb
```

---

## 📁 Repository Providers

The repository provider controls where the server reads project files from. Defaults to `local`.

Supported values: `local`, `github`, `gitlab`, `gitea`

---

### Local Filesystem (Default)

Reads files from the local filesystem. No additional configuration required.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_PROVIDER` | `local` | Set to `local` or omit |
| `PROJECT_PATH` | _(from tool call)_ | Override the project path at server startup |

---

### GitHub

Reads files from GitHub repositories via the GitHub REST API.

**Getting a Personal Access Token:**

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)** or **Fine-grained personal access tokens**
   - Classic: grant the `repo` scope (or `public_repo` for public repositories only)
   - Fine-grained: grant **Contents: Read-only** on the target repositories
3. Copy the generated token

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_PROVIDER` | `local` | Must be set to `github` |
| `REPO_AUTH_TOKEN` | _(empty)_ | GitHub personal access token. Required for private repos |
| `REPO_BASE_URL` | `https://api.github.com` | Override for GitHub Enterprise Server |
| `REPO_DEFAULT_BRANCH` | `main` | Default branch when none is specified |

**Example:**

```bash
export REPO_PROVIDER=github
export REPO_AUTH_TOKEN=ghp_...

# GitHub Enterprise only:
export REPO_BASE_URL=https://github.example.com/api/v3
```

---

### GitLab

Reads files from GitLab repositories via the GitLab REST API.

**Getting a Personal Access Token:**

1. Navigate to **User Settings → Access Tokens** (profile menu → Edit profile → Access Tokens)
2. Click **Add new token**
3. Grant at minimum the `read_api` scope
4. Set an expiry date and click **Create personal access token**
5. Copy the token immediately — it is not shown again

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_PROVIDER` | `local` | Must be set to `gitlab` |
| `REPO_AUTH_TOKEN` | _(empty)_ | GitLab personal access token |
| `REPO_BASE_URL` | `https://gitlab.com` | Override for self-hosted GitLab instances |
| `REPO_DEFAULT_BRANCH` | `main` | Default branch when none is specified |

**Example:**

```bash
export REPO_PROVIDER=gitlab
export REPO_AUTH_TOKEN=glpat-...

# Self-hosted GitLab only:
export REPO_BASE_URL=https://gitlab.example.com
```

---

### Gitea

Reads files from self-hosted Gitea instances. `REPO_BASE_URL` is required.

**Getting an Access Token:**

1. Log in to your Gitea instance
2. Go to **Settings → Applications** (your user avatar → Settings → Applications)
3. Under **Manage Access Tokens**, enter a name, select the desired permissions, and click **Generate Token**
4. Copy the generated token — it is only shown once

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_PROVIDER` | `local` | Must be set to `gitea` |
| `REPO_BASE_URL` | — | **Required.** Your Gitea instance URL (e.g. `https://gitea.example.com`) |
| `REPO_AUTH_TOKEN` | _(empty)_ | Gitea access token |
| `REPO_DEFAULT_BRANCH` | `main` | Default branch when none is specified |

**Example:**

```bash
export REPO_PROVIDER=gitea
export REPO_BASE_URL=https://gitea.example.com
export REPO_AUTH_TOKEN=...
```

---

### Multi-Tenant Mode

All repository providers support multi-tenant mode, which restricts file access to an allowlist of approved organizations and repositories. Enable it with `REPO_MULTI_TENANT=true`.

At least one of `APPROVED_ORGS` or `APPROVED_REPOS` must be set when multi-tenant mode is active.

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_MULTI_TENANT` | `false` | Set to `true` to enable allowlist enforcement |
| `APPROVED_ORGS` | _(none)_ | Comma-separated list of approved organization names |
| `APPROVED_REPOS` | _(none)_ | Comma-separated list of approved `owner/repo` identifiers |

**Example:**

```bash
export REPO_MULTI_TENANT=true
export APPROVED_ORGS=my-org,partner-org
export APPROVED_REPOS=other-org/specific-repo
```

---

## 🚌 Transport

The transport is selected by the `MCP_TRANSPORT` environment variable. Defaults to `stdio`.

---

### stdio (Default)

Standard input/output transport. Compatible with Claude Desktop, Claude Code, Cursor, Continue, VS Code Copilot, and most other MCP clients. No additional installation or configuration required.

```bash
export MCP_TRANSPORT=stdio  # Optional — this is the default
project-context-server
```

---

### HTTP/SSE

HTTP/SSE transport for remote deployments, team servers, and cloud integrations.

**Install:**

```bash
pip install "mcp-project-context-server[sse]"
```

**Start the server:**

```bash
export MCP_TRANSPORT=sse
export MCP_HOST=0.0.0.0  # Optional — default is 0.0.0.0
export MCP_PORT=8080      # Optional — default is 8080
project-context-server
```

The server exposes two endpoints:
- `GET /sse` — SSE connection endpoint for MCP clients
- `GET /health` — unauthenticated health check

**Authentication:**

| `MCP_AUTH_TYPE` | Description |
|-----------------|-------------|
| `none` | No authentication. Use only on trusted private networks. |
| `bearer` | Static token via `Authorization: Bearer <token>`. Requires `MCP_AUTH_TOKEN`. |
| `google-iam` | Google Cloud identity token validation. For use with Agent Engine and service-to-service calls. |

**Bearer token example:**

```bash
export MCP_TRANSPORT=sse
export MCP_AUTH_TYPE=bearer
export MCP_AUTH_TOKEN=your-secret-token
project-context-server
```

**Google IAM example:**

```bash
export MCP_TRANSPORT=sse
export MCP_AUTH_TYPE=google-iam
export GOOGLE_IAM_AUDIENCE=https://my-service.example.com     # Recommended
export GOOGLE_APPROVED_SERVICE_ACCOUNTS=sa@project.iam.gserviceaccount.com  # Optional allowlist
project-context-server
```

**SSE environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio` | Must be set to `sse` |
| `MCP_HOST` | `0.0.0.0` | Bind address |
| `MCP_PORT` | `8080` | Listen port |
| `MCP_AUTH_TYPE` | `none` | Authentication: `none`, `bearer`, `google-iam` |
| `MCP_AUTH_TOKEN` | — | Required when `MCP_AUTH_TYPE=bearer` |
| `GOOGLE_IAM_AUDIENCE` | _(none)_ | Expected `aud` claim in Google identity tokens |
| `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` | _(none)_ | Path to service account JSON key (uses ADC if unset) |
| `GOOGLE_APPROVED_SERVICE_ACCOUNTS` | _(none)_ | Comma-separated allowed caller service account emails |

---

## 🖥️ Client Setup

The examples below use **Ollama** as the embedding provider and **ChromaDB local** as the vector store — the simplest setup with no API key requirements. Substitute environment variables for your chosen providers using the reference in [Embedding Providers](#-embedding-providers) and [Vector Stores](#️-vector-stores).

> **Detailed client docs** with full per-provider configuration matrices are available in [`docs/clients/`](docs/clients/). Those docs are currently being updated to correct some environment variable names from the old implementation — see [`docs/client-setup-expansion.md`](docs/client-setup-expansion.md) for status and the correct variable reference.

---

### Claude Desktop

1. **Install the server:**

   ```bash
   pip install "mcp-project-context-server[ollama]"
   ```

2. **Locate the config file** for your OS:

   | OS | Config File |
   |----|-------------|
   | **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
   | **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
   | **Linux** | `~/.config/Claude/claude_desktop_config.json` |

3. **Add the server** to `claude_desktop_config.json`:

   **Windows:**

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
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
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** and verify the server appears in the MCP tools list.

---

### Claude Code

1. **Install the server:**

   ```bash
   pip install "mcp-project-context-server[ollama]"
   ```

2. **Add the MCP server** using one of two methods:

   **Option A — CLI:**

   ```bash
   claude mcp add project-context \
     -e EMBED_PROVIDER=ollama \
     -e OLLAMA_HOST=http://localhost:11434 \
     -e OLLAMA_EMBED_MODEL=nomic-embed-text \
     -- python -m mcp_project_context_server
   ```

   **Option B — Config file:**

   | Scope | Location |
   |-------|----------|
   | **User (global)** | `~/.claude.json` |
   | **Project** | `.claude/settings.json` (in project root) |

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

3. **Verify the server is connected:**

   ```bash
   claude mcp list
   ```

---

### Cursor

1. **Install the server** (see [Installation](#-installation))

2. **Choose a config scope:**

   | Scope | Windows | macOS / Linux |
   |-------|---------|---------------|
   | **Global** | `%USERPROFILE%\.cursor\mcp.json` | `~/.cursor/mcp.json` |
   | **Project** | `.cursor\mcp.json` (project root) | `.cursor/mcp.json` (project root) |

3. **Configure `mcp.json`:**

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

4. **Reload Cursor** and use `@project-context` in the chat panel.

---

### Continue

1. **Install the Continue extension** for VS Code or JetBrains

2. **Locate the config file:**

   | OS | Config File |
   |----|-------------|
   | **Windows** | `%USERPROFILE%\.continue\config.yaml` |
   | **macOS / Linux** | `~/.continue/config.yaml` |

3. **Add to `config.yaml`:**

   ```yaml
   mcpServers:
     - name: project-context
       command: python
       args:
         - "-m"
         - mcp_project_context_server
       env:
         EMBED_PROVIDER: "ollama"
         OLLAMA_HOST: "http://localhost:11434"
         OLLAMA_EMBED_MODEL: "nomic-embed-text"
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
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     ]
   }
   ```

---

### Windsurf

1. **Install the server** (see [Installation](#-installation))

2. **Locate the MCP config file:**

   | OS | Config File |
   |----|-------------|
   | **Windows** | `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
   | **macOS / Linux** | `~/.codeium/windsurf/mcp_config.json` |

3. **Configure `mcp_config.json`** (create if it does not exist):

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

4. **Restart Windsurf** and verify the server appears under **Settings → MCP Servers**.

---

### VS Code Copilot

MCP support is built into VS Code via **GitHub Copilot** (no separate extension required). Requires VS Code 1.99+ with the Copilot extension.

1. **Install the server** (see [Installation](#-installation))

2. **Choose a config scope:**

   **Option A — Workspace (`.vscode/mcp.json`):**

   ```json
   {
     "servers": {
       "project-context": {
         "type": "stdio",
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

   **Option B — User settings (`settings.json`):**

   ```json
   {
     "mcp": {
       "servers": {
         "project-context": {
           "type": "stdio",
           "command": "python",
           "args": ["-m", "mcp_project_context_server"],
           "env": {
             "EMBED_PROVIDER": "ollama",
             "OLLAMA_HOST": "http://localhost:11434",
             "OLLAMA_EMBED_MODEL": "nomic-embed-text"
           }
         }
       }
     }
   }
   ```

3. **Use in Copilot Chat** by switching to **Agent mode** — MCP tools are available automatically.

---

## 🛠️ Tools Reference

| Tool | Description |
|------|-------------|
| `index_project_context` | Indexes all files in `.context/` into the configured vector store |
| `search_project_context` | Performs semantic search over indexed context |
| `load_project_context` | Returns the full contents of `.context/` (project overview, ADRs, latest session) |
| `save_session_summary` | Writes a session note to `.context/sessions/YYYY-MM-DD.md` |
| `list_repositories` | Lists available repositories via the configured repository provider |

### Usage Examples

```python
# Semantic search
search_project_context(
    query="How do we handle authentication?",
    n_results=5
)

# Load full context
load_project_context()
# Returns: project.md, all ADRs, latest session file

# Save session notes
save_session_summary(
    summary="Investigated chunking strategy alternatives, decided on fixed-size for now"
)

# Rebuild the index
index_project_context()
```

---

## 🌐 Environment Variables Reference

### Embedding Providers

| Variable | Provider | Default | Required |
|----------|----------|---------|----------|
| `EMBED_PROVIDER` | All | — | Yes |
| `OLLAMA_HOST` | `ollama` | `http://localhost:11434` | No |
| `OLLAMA_EMBED_MODEL` | `ollama` | `nomic-embed-text` | No |
| `VOYAGE_API_KEY` | `voyage` | — | Yes |
| `VOYAGE_EMBED_MODEL` | `voyage` | `voyage-code-3` | No |
| `OPENAI_API_KEY` | `openai` | — | Yes |
| `OPENAI_EMBED_MODEL` | `openai` | `text-embedding-3-small` | No |
| `COHERE_API_KEY` | `cohere` | — | Yes |
| `COHERE_EMBED_MODEL` | `cohere` | `embed-english-v3.0` | No |
| `GOOGLE_API_KEY` | `google` | — | Yes |
| `GOOGLE_EMBED_MODEL` | `google` | `text-embedding-004` | No |
| `VERTEXAI_PROJECT` | `vertexai` | — | Yes |
| `VERTEXAI_LOCATION` | `vertexai` | — | Yes |
| `VERTEXAI_EMBED_MODEL` | `vertexai` | `text-embedding-004` | No |

### Vector Stores

| Variable | Store | Default | Required |
|----------|-------|---------|----------|
| `VECTOR_STORE_PROVIDER` | All | `chroma-local` | No |
| `CHROMA_DIR` | `chroma-local` | `~/.mcp-data/chroma` | No |
| `CHROMA_HOST` | `chroma-http` | `localhost` | No |
| `CHROMA_PORT` | `chroma-http` | `8000` | No |
| `CHROMA_API_KEY` | `chroma-http` | _(none)_ | No |
| `PGVECTOR_CONNECTION_STRING` | `pgvector` | — | Yes (for pgvector) |

### Repository Providers

| Variable | Provider | Default | Required |
|----------|----------|---------|----------|
| `REPO_PROVIDER` | All | `local` | No |
| `PROJECT_PATH` | `local` | _(from tool call)_ | No |
| `REPO_AUTH_TOKEN` | `github`, `gitlab`, `gitea` | _(empty)_ | No (required for private repos) |
| `REPO_BASE_URL` | `github`, `gitlab`, `gitea` | _(provider default)_ | Yes for `gitea` |
| `REPO_DEFAULT_BRANCH` | `github`, `gitlab`, `gitea` | `main` | No |
| `REPO_MULTI_TENANT` | All | `false` | No |
| `APPROVED_ORGS` | All (multi-tenant) | _(none)_ | Yes (if multi-tenant, with no APPROVED_REPOS) |
| `APPROVED_REPOS` | All (multi-tenant) | _(none)_ | Yes (if multi-tenant, with no APPROVED_ORGS) |

### Transport

| Variable | Default | Required |
|----------|---------|----------|
| `MCP_TRANSPORT` | `stdio` | No |
| `MCP_HOST` | `0.0.0.0` | No |
| `MCP_PORT` | `8080` | No |
| `MCP_AUTH_TYPE` | `none` | No |
| `MCP_AUTH_TOKEN` | — | Yes (if `MCP_AUTH_TYPE=bearer`) |
| `GOOGLE_IAM_AUDIENCE` | _(none)_ | No |
| `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` | _(none)_ | No |
| `GOOGLE_APPROVED_SERVICE_ACCOUNTS` | _(none)_ | No |

---

## 📂 Project Structure

```
mcp-project-context-server/
├── src/mcp_project_context_server/
│   ├── server.py                       # MCP server entry point and tool registry
│   ├── exceptions.py                   # Shared exception types
│   ├── tools/
│   │   ├── index_context.py            # index_project_context tool
│   │   ├── search_context.py           # search_project_context tool
│   │   ├── load_context.py             # load_project_context tool
│   │   ├── save_session.py             # save_session_summary tool
│   │   └── list_repositories.py        # list_repositories tool
│   ├── integrations/
│   │   ├── embeddings/
│   │   │   ├── base.py                 # EmbeddingProvider Protocol
│   │   │   ├── registry.py             # Provider factory (EMBED_PROVIDER)
│   │   │   ├── ollama/client.py
│   │   │   ├── voyage/client.py
│   │   │   ├── openai/client.py
│   │   │   ├── cohere/client.py
│   │   │   ├── google/client.py
│   │   │   └── vertexai/client.py
│   │   ├── vectorstore/
│   │   │   ├── base.py                 # VectorStoreProvider Protocol
│   │   │   ├── registry.py             # Provider factory (VECTOR_STORE_PROVIDER)
│   │   │   ├── chroma_local/client.py
│   │   │   ├── chroma_http/client.py
│   │   │   └── pgvector/client.py
│   │   ├── repository/
│   │   │   ├── base.py                 # RepositoryProvider Protocol
│   │   │   ├── registry.py             # Provider factory (REPO_PROVIDER)
│   │   │   ├── local/client.py
│   │   │   ├── github/client.py
│   │   │   ├── gitlab/client.py
│   │   │   └── gitea/client.py
│   │   └── transport/
│   │       ├── stdio.py
│   │       └── sse.py
│   └── helpers/
│       └── context.py                  # Utility functions
├── .context/                            # Project context directory
│   ├── project.md                      # Project overview
│   ├── sessions/                       # Session notes
│   └── decisions/                      # Architecture Decision Records
├── tests/
│   ├── unit/                           # Unit tests (mocked dependencies)
│   └── integration/                    # Integration tests (real services)
├── docs/
│   └── client-setup-expansion.md       # Per-provider client setup expansion plan
├── README.md
├── CONTRIBUTING.md
├── pyproject.toml
└── LICENSE
```

---

## 🧪 Testing

### Run the Test Suite

```bash
# Install test dependencies
pip install "mcp-project-context-server[all]"
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Unit tests (no external services required)
pytest tests/unit/

# Integration tests (requires a running embedding provider and vector store)
pytest tests/integration/

# All tests with coverage report
pytest --cov=src/mcp_project_context_server tests/
```

### Development Workflow

```bash
# Format and lint
black src/
isort src/
flake8 src/
mypy src/

# Check coverage
pytest --cov=src/mcp_project_context_server --cov-report=term-missing tests/unit/
```

---

## 🔮 Roadmap

- [ ] **Auto-reindex**: Watchdog-based file monitoring for automatic reindexing
- [ ] **Codebase Indexing**: Repomix integration for source code analysis
- [ ] **Enhanced ADR Tools**: First-class MCP tools for ADR lifecycle management
- [ ] **Batch Operations**: Bulk ADR updates and session imports
- [ ] **Provider Caching**: Singleton caching for embedding and vector store providers

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines including commit message standards, ADR requirements, and the PR process.

---

## 📝 License

This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE Version 3 — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **MCP Team**: For the Model Context Protocol
- **ChromaDB**: For the embedded vector store
- **Ollama**: For local embedding model hosting

---

<div align="center">

**Built with ❤️ for better LLM project understanding**

</div>
