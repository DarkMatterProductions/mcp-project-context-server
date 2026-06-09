# Configuration Reference

This page is the authoritative reference for every environment variable understood by `mcp-project-context-server`. All configuration is done entirely through environment variables — there are no config files on the server side.

---

## Table of Contents

1. [Embedding Providers](#1-embedding-providers)
2. [Vector Store Providers](#2-vector-store-providers)
3. [Repository Providers](#3-repository-providers)
4. [Transport & Authentication](#4-transport--authentication)

---

## 1. Embedding Providers

Set `EMBED_PROVIDER` to choose which embedding backend generates vector representations of your code and documentation.

```bash
EMBED_PROVIDER=ollama   # default — fully local, no API key required
```

| Provider value | Extra install | API key required |
|---|---|---|
| `ollama` | *(base)* | No |
| `voyage` | `[voyage]` | Yes — [voyageai.com](https://www.voyageai.com) |
| `openai` | `[openai]` | Yes — [platform.openai.com](https://platform.openai.com) |
| `cohere` | `[cohere]` | Yes — [cohere.com](https://cohere.com) |
| `google` | `[google]` | Yes — [aistudio.google.com](https://aistudio.google.com) |
| `google-vertex` | `[google-vertex]` | No key — uses ADC/service account |

---

### 1.1 `ollama`

Runs entirely on your local machine via [Ollama](https://ollama.com). No API key or internet access required.

| Variable | Required | Default | Description |
|---|---|---|---|
| `EMBED_PROVIDER` | Yes | — | Set to `ollama` |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Base URL of the Ollama server |
| `OLLAMA_EMBED_MODEL` | No | `nomic-embed-text` | Model name to use for embeddings |

**Notes:**
- Pull the model before first use: `ollama pull nomic-embed-text`
- Other strong local options: `mxbai-embed-large`, `bge-m3`
- The Ollama server must be running (`ollama serve`) before starting the MCP server

**Example:**
```bash
EMBED_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

### 1.2 `voyage`

[Voyage AI](https://www.voyageai.com) provides state-of-the-art embeddings purpose-built for code retrieval.

| Variable | Required | Default | Description |
|---|---|---|---|
| `EMBED_PROVIDER` | Yes | — | Set to `voyage` |
| `VOYAGE_API_KEY` | Yes | — | API key from [dash.voyageai.com/api-keys](https://dash.voyageai.com/api-keys) |
| `VOYAGE_EMBED_MODEL` | No | `voyage-code-3` | Model name |

**Notes:**
- `voyage-code-3` is the recommended model for code-heavy repositories
- Install extra: `pip install "mcp-project-context-server[voyage]"`

**Example:**
```bash
EMBED_PROVIDER=voyage
VOYAGE_API_KEY=pa-...
VOYAGE_EMBED_MODEL=voyage-code-3
```

---

### 1.3 `openai`

Uses the [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings).

| Variable | Required | Default | Description |
|---|---|---|---|
| `EMBED_PROVIDER` | Yes | — | Set to `openai` |
| `OPENAI_API_KEY` | Yes | — | API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `OPENAI_EMBED_MODEL` | No | `text-embedding-3-small` | Model name |
| `OPENAI_EMBED_DIMENSIONS` | No | *(model default)* | Override output dimensions (supported by `text-embedding-3-*` models) |

**Notes:**
- `text-embedding-3-large` offers higher quality at higher cost
- Install extra: `pip install "mcp-project-context-server[openai]"`

**Example:**
```bash
EMBED_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_EMBED_MODEL=text-embedding-3-small
```

---

### 1.4 `cohere`

Uses the [Cohere Embed API](https://docs.cohere.com/reference/embed).

| Variable | Required | Default | Description |
|---|---|---|---|
| `EMBED_PROVIDER` | Yes | — | Set to `cohere` |
| `COHERE_API_KEY` | Yes | — | API key from [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys) |
| `COHERE_EMBED_MODEL` | No | `embed-english-v3.0` | Model name |

**Notes:**
- For multilingual codebases consider `embed-multilingual-v3.0`
- Install extra: `pip install "mcp-project-context-server[cohere]"`

**Example:**
```bash
EMBED_PROVIDER=cohere
COHERE_API_KEY=...
COHERE_EMBED_MODEL=embed-english-v3.0
```

---

### 1.5 `google`

Uses the [Google Gemini Embedding API](https://ai.google.dev/gemini-api/docs/embeddings) via `GOOGLE_API_KEY` (AI Studio key).

| Variable | Required | Default | Description |
|---|---|---|---|
| `EMBED_PROVIDER` | Yes | — | Set to `google` |
| `GOOGLE_API_KEY` | Yes | — | API key from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `GOOGLE_EMBED_MODEL` | No | `text-embedding-004` | Gemini embedding model name |

**Notes:**
- Install extra: `pip install "mcp-project-context-server[google]"`
- This uses the public Gemini API, not Vertex AI. For Vertex AI, use `google-vertex`

**Example:**
```bash
EMBED_PROVIDER=google
GOOGLE_API_KEY=AIza...
GOOGLE_EMBED_MODEL=text-embedding-004
```

---

### 1.6 `google-vertex`

Uses [Vertex AI Text Embeddings](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings) with Application Default Credentials (ADC) or a service account key. Recommended for GCP-hosted deployments.

| Variable | Required | Default | Description |
|---|---|---|---|
| `EMBED_PROVIDER` | Yes | — | Set to `google-vertex` |
| `GOOGLE_CLOUD_PROJECT` | Yes | — | GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | No | `us-central1` | Vertex AI region |
| `VERTEX_EMBED_MODEL` | No | `text-embedding-005` | Vertex AI embedding model |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | *(ADC default)* | Path to service account JSON key file (if not using Workload Identity or `gcloud auth`) |

**Notes:**
- Install extra: `pip install "mcp-project-context-server[google-vertex]"`
- When running on GCE/Cloud Run with a service account attached, ADC is used automatically — no key file needed
- Run `gcloud auth application-default login` for local development

**Example:**
```bash
EMBED_PROVIDER=google-vertex
GOOGLE_CLOUD_PROJECT=my-gcp-project
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_EMBED_MODEL=text-embedding-005
```

---

## 2. Vector Store Providers

Set `VECTOR_STORE_PROVIDER` to choose where embeddings are stored and searched.

```bash
VECTOR_STORE_PROVIDER=chroma-local   # default
```

---

### 2.1 `chroma-local` *(default)*

Persists a [ChromaDB](https://www.trychroma.com/) database to a local directory. Zero infrastructure required. Best for single-developer use.

| Variable | Required | Default | Description |
|---|---|---|---|
| `VECTOR_STORE_PROVIDER` | No | `chroma-local` | Set to `chroma-local` to be explicit |
| `CHROMA_PERSIST_DIR` | No | `~/.mcp-project-context/chroma` | Directory where ChromaDB data is persisted |

**When to use:** Local development, single developer, no shared infrastructure.

**Example:**
```bash
VECTOR_STORE_PROVIDER=chroma-local
CHROMA_PERSIST_DIR=/data/chroma
```

---

### 2.2 `chroma-http`

Connects to a remote [ChromaDB HTTP server](https://docs.trychroma.com/production/containers/docker). Allows multiple server instances to share the same index.

| Variable | Required | Default | Description |
|---|---|---|---|
| `VECTOR_STORE_PROVIDER` | Yes | — | Set to `chroma-http` |
| `CHROMA_HTTP_HOST` | Yes | — | Hostname or IP of the ChromaDB server |
| `CHROMA_HTTP_PORT` | No | `8000` | Port of the ChromaDB server |
| `CHROMA_HTTP_SSL` | No | `false` | Set to `true` to use HTTPS |
| `CHROMA_HTTP_HEADERS` | No | — | JSON string of additional HTTP headers (e.g., for auth) |

**When to use:** Small team server, shared index, when you want vector storage separated from the MCP server process.

**Example:**
```bash
VECTOR_STORE_PROVIDER=chroma-http
CHROMA_HTTP_HOST=chroma.internal.example.com
CHROMA_HTTP_PORT=8000
CHROMA_HTTP_SSL=false
```

---

### 2.3 `pgvector`

Uses [pgvector](https://github.com/pgvector/pgvector) extension in PostgreSQL. Recommended for team and enterprise deployments.

| Variable | Required | Default | Description |
|---|---|---|---|
| `VECTOR_STORE_PROVIDER` | Yes | — | Set to `pgvector` |
| `PGVECTOR_CONNECTION_STRING` | Yes | — | PostgreSQL DSN (see below) |
| `PGVECTOR_TABLE_NAME` | No | `project_context_embeddings` | Table name for storing embeddings |

**Connection string format:**
```
postgresql://user:password@host:5432/dbname
```

**When to use:** Team servers, enterprise deployments, when you need durable shared storage, full ACID guarantees, or are already running PostgreSQL.

**Prerequisites:** PostgreSQL ≥ 14 with `pgvector` extension installed:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Install extra:** `pip install "mcp-project-context-server[pgvector]"`

**Example:**
```bash
VECTOR_STORE_PROVIDER=pgvector
PGVECTOR_CONNECTION_STRING=postgresql://mcpuser:secret@db.internal:5432/mcp_context
```

---

## 3. Repository Providers

Set `REPO_PROVIDER` to tell the server how to fetch source code when a tool receives a `project_path` argument.

```bash
REPO_PROVIDER=local   # default
```

---

### 3.1 `local` *(default)*

Reads from the local filesystem. `project_path` must be an absolute or relative filesystem path.

| Variable | Required | Default | Description |
|---|---|---|---|
| `REPO_PROVIDER` | No | `local` | Set to `local` to be explicit |

**`project_path` format:** Absolute or relative filesystem path, e.g. `/home/user/my-project` or `./my-project`

---

### 3.2 `github`

Fetches repositories from [GitHub](https://github.com) via the GitHub API and/or Git over HTTPS.

| Variable | Required | Default | Description |
|---|---|---|---|
| `REPO_PROVIDER` | Yes | — | Set to `github` |
| `GITHUB_TOKEN` | Yes | — | Personal Access Token or GitHub App token. Create at [github.com/settings/tokens](https://github.com/settings/tokens). Requires `repo` (or `public_repo`) scope |
| `GITHUB_BASE_URL` | No | `https://api.github.com` | Override for GitHub Enterprise Server |

**`project_path` format:**
- Short form: `owner/repo` (e.g., `acme/backend`)
- Full URL: `https://github.com/owner/repo`

---

### 3.3 `gitlab`

Fetches repositories from [GitLab](https://gitlab.com) or a self-hosted GitLab instance.

| Variable | Required | Default | Description |
|---|---|---|---|
| `REPO_PROVIDER` | Yes | — | Set to `gitlab` |
| `GITLAB_TOKEN` | Yes | — | Personal Access Token or Project Access Token. Create at **Settings → Access Tokens** in GitLab. Requires `read_repository` scope |
| `GITLAB_BASE_URL` | No | `https://gitlab.com` | Override for self-hosted GitLab (e.g., `https://gitlab.internal.example.com`) |

**`project_path` format:**
- Short form: `namespace/repo` (e.g., `acme/backend`, or `acme/team/backend` for nested groups)
- Full URL: `https://gitlab.com/namespace/repo`

---

### 3.4 `gitea`

Fetches repositories from a [Gitea](https://about.gitea.com/) instance.

| Variable | Required | Default | Description |
|---|---|---|---|
| `REPO_PROVIDER` | Yes | — | Set to `gitea` |
| `GITEA_TOKEN` | Yes | — | API token from your Gitea profile under **Settings → Applications** |
| `GITEA_BASE_URL` | Yes | — | Base URL of your Gitea server (e.g., `https://gitea.internal.example.com`) |

**`project_path` format:**
- Short form: `owner/repo`
- Full URL: `https://gitea.internal.example.com/owner/repo`

---

### 3.5 Multi-Tenant Mode

Multi-tenant mode allows a **single server deployment** to serve multiple organizations. This is primarily used with HTTP/SSE transport in team or enterprise scenarios.

| Variable | Required | Default | Description |
|---|---|---|---|
| `REPO_MULTI_TENANT` | No | `false` | Set to `true` to enable multi-tenant mode |
| `APPROVED_ORGS` | No | *(all)* | Comma-separated list of organization/namespace names that callers are allowed to index. E.g., `acme,acme-labs` |
| `APPROVED_REPOS` | No | *(all in approved orgs)* | Comma-separated allow-list of specific `owner/repo` pairs. E.g., `acme/backend,acme/frontend` |

**How it works:**
- When `REPO_MULTI_TENANT=true`, the server exposes a `list_repositories` tool that lets agents discover which repos are available
- `APPROVED_ORGS` restricts which organizations can be queried
- `APPROVED_REPOS` provides fine-grained control on top of `APPROVED_ORGS`
- If neither is set (with multi-tenant enabled), all repos accessible to the token can be indexed — use with caution

**Example:**
```bash
REPO_PROVIDER=github
REPO_MULTI_TENANT=true
APPROVED_ORGS=acme,acme-labs
APPROVED_REPOS=acme/backend,acme/frontend,acme-labs/infra
GITHUB_TOKEN=ghp_...
```

---

## 4. Transport & Authentication

### 4.1 `stdio` *(default)*

Standard input/output transport. The MCP client launches the server as a subprocess and communicates over stdin/stdout. This is the correct mode for all local desktop clients (Claude Desktop, Cursor, VS Code Copilot, etc.).

| Variable | Required | Default | Description |
|---|---|---|---|
| `MCP_TRANSPORT` | No | `stdio` | Set to `stdio` to be explicit |

**Notes:**
- No network port is opened
- `MCP_AUTH_TYPE` is ignored in stdio mode — the OS process isolation provides security
- The server entry point is `project-context-server`

---

### 4.2 `sse` (HTTP/SSE transport)

Server-Sent Events over HTTP. The server listens on a TCP port and clients connect over the network. Required for team servers, cloud deployments, and Agent Engine.

Install extra: `pip install "mcp-project-context-server[sse]"`

| Variable | Required | Default | Description |
|---|---|---|---|
| `MCP_TRANSPORT` | Yes | — | Set to `sse` |
| `MCP_HOST` | No | `0.0.0.0` | Interface to bind to |
| `MCP_PORT` | No | `8080` | TCP port to listen on |
| `MCP_AUTH_TYPE` | No | `none` | Authentication mode: `none`, `bearer`, or `google-iam` |

---

### 4.3 Bearer Token Auth (`MCP_AUTH_TYPE=bearer`)

Simple shared-secret authentication for team servers. Every HTTP request must carry an `Authorization: Bearer <token>` header.

| Variable | Required | Default | Description |
|---|---|---|---|
| `MCP_AUTH_TYPE` | Yes | — | Set to `bearer` |
| `MCP_AUTH_TOKEN` | Yes | — | The shared secret token. Choose a strong random value (e.g., `openssl rand -hex 32`) |

**Example:**
```bash
MCP_TRANSPORT=sse
MCP_HOST=0.0.0.0
MCP_PORT=8080
MCP_AUTH_TYPE=bearer
MCP_AUTH_TOKEN=a4f2c8...   # output of: openssl rand -hex 32
```

---

### 4.4 Google IAM Auth (`MCP_AUTH_TYPE=google-iam`)

Validates [Google-signed OIDC tokens](https://cloud.google.com/run/docs/authenticating/service-to-service) from calling service accounts. Recommended for Cloud Run / Agent Engine deployments.

| Variable | Required | Default | Description |
|---|---|---|---|
| `MCP_AUTH_TYPE` | Yes | — | Set to `google-iam` |
| `GOOGLE_IAM_AUDIENCE` | Yes | — | Expected `aud` claim in the OIDC token — typically the Cloud Run service URL (e.g., `https://mcp-context-abc123-uc.a.run.app`) |
| `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` | No | *(ADC)* | Path to a service account JSON key for verifying tokens. Not needed when running on GCP (uses metadata server) |
| `GOOGLE_APPROVED_SERVICE_ACCOUNTS` | No | *(any valid token)* | Comma-separated list of service account email addresses that are authorized to call this server. E.g., `agent@project.iam.gserviceaccount.com` |

**Example:**
```bash
MCP_TRANSPORT=sse
MCP_AUTH_TYPE=google-iam
GOOGLE_IAM_AUDIENCE=https://mcp-context-abc123-uc.a.run.app
GOOGLE_APPROVED_SERVICE_ACCOUNTS=vertex-agent@my-gcp-project.iam.gserviceaccount.com
```

---

## Complete Variable Index

| Variable | Section | Default |
|---|---|---|
| `EMBED_PROVIDER` | Embeddings | `ollama` |
| `OLLAMA_BASE_URL` | Embeddings / ollama | `http://localhost:11434` |
| `OLLAMA_EMBED_MODEL` | Embeddings / ollama | `nomic-embed-text` |
| `VOYAGE_API_KEY` | Embeddings / voyage | — |
| `VOYAGE_EMBED_MODEL` | Embeddings / voyage | `voyage-code-3` |
| `OPENAI_API_KEY` | Embeddings / openai | — |
| `OPENAI_EMBED_MODEL` | Embeddings / openai | `text-embedding-3-small` |
| `OPENAI_EMBED_DIMENSIONS` | Embeddings / openai | *(model default)* |
| `COHERE_API_KEY` | Embeddings / cohere | — |
| `COHERE_EMBED_MODEL` | Embeddings / cohere | `embed-english-v3.0` |
| `GOOGLE_API_KEY` | Embeddings / google | — |
| `GOOGLE_EMBED_MODEL` | Embeddings / google | `text-embedding-004` |
| `GOOGLE_CLOUD_PROJECT` | Embeddings / google-vertex | — |
| `GOOGLE_CLOUD_LOCATION` | Embeddings / google-vertex | `us-central1` |
| `VERTEX_EMBED_MODEL` | Embeddings / google-vertex | `text-embedding-005` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Embeddings / google-vertex | *(ADC)* |
| `VECTOR_STORE_PROVIDER` | Vector Store | `chroma-local` |
| `CHROMA_PERSIST_DIR` | Vector Store / chroma-local | `~/.mcp-project-context/chroma` |
| `CHROMA_HTTP_HOST` | Vector Store / chroma-http | — |
| `CHROMA_HTTP_PORT` | Vector Store / chroma-http | `8000` |
| `CHROMA_HTTP_SSL` | Vector Store / chroma-http | `false` |
| `CHROMA_HTTP_HEADERS` | Vector Store / chroma-http | — |
| `PGVECTOR_CONNECTION_STRING` | Vector Store / pgvector | — |
| `PGVECTOR_TABLE_NAME` | Vector Store / pgvector | `project_context_embeddings` |
| `REPO_PROVIDER` | Repository | `local` |
| `GITHUB_TOKEN` | Repository / github | — |
| `GITHUB_BASE_URL` | Repository / github | `https://api.github.com` |
| `GITLAB_TOKEN` | Repository / gitlab | — |
| `GITLAB_BASE_URL` | Repository / gitlab | `https://gitlab.com` |
| `GITEA_TOKEN` | Repository / gitea | — |
| `GITEA_BASE_URL` | Repository / gitea | — |
| `REPO_MULTI_TENANT` | Repository / multi-tenant | `false` |
| `APPROVED_ORGS` | Repository / multi-tenant | *(all)* |
| `APPROVED_REPOS` | Repository / multi-tenant | *(all)* |
| `MCP_TRANSPORT` | Transport | `stdio` |
| `MCP_HOST` | Transport / sse | `0.0.0.0` |
| `MCP_PORT` | Transport / sse | `8080` |
| `MCP_AUTH_TYPE` | Transport / sse | `none` |
| `MCP_AUTH_TOKEN` | Transport / bearer | — |
| `GOOGLE_IAM_AUDIENCE` | Transport / google-iam | — |
| `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` | Transport / google-iam | *(ADC)* |
| `GOOGLE_APPROVED_SERVICE_ACCOUNTS` | Transport / google-iam | *(any valid)* |
