# Deployment Topologies

This guide walks through three complete, end-to-end deployment scenarios for `mcp-project-context-server`. Choose the topology that matches your use case:

| Topology | Best for | Transport | Vector store | Auth |
|---|---|---|---|---|
| [1. Local Developer](#topology-1-local-developer) | Individual developer, single machine | STDIO | chroma-local | None (OS isolation) |
| [2. Team Server](#topology-2-team-server) | Small–medium team, shared server | HTTP/SSE | pgvector | Bearer token |
| [3. Enterprise / Agent Engine](#topology-3-enterprise--agent-engine) | Large org, GCP-native, multi-tenant | HTTP/SSE | pgvector | Google IAM |

---

## Topology 1: Local Developer

**Stack:** STDIO + `local` repo provider + `chroma-local` vector store

This is the simplest setup. The server runs as a subprocess of your MCP client (e.g., Claude Desktop), reads code from your local filesystem, stores embeddings locally, and requires no infrastructure beyond your development machine.

---

### Step 1 — Install

Choose your embedding provider. Two strong options for local development:

**Option A: Ollama (completely free, no API key)**
```bash
# Install Ollama: https://ollama.com
# Then install the MCP server (base package is enough)
pip install mcp-project-context-server

# Pull the embedding model
ollama pull nomic-embed-text

# Start the Ollama server (if not already running as a background service)
ollama serve
```

**Option B: Voyage AI (best retrieval quality for code)**
```bash
pip install "mcp-project-context-server[voyage]"
# Get API key at: https://dash.voyageai.com/api-keys
```

**Option C: OpenAI**
```bash
pip install "mcp-project-context-server[openai]"
# Get API key at: https://platform.openai.com/api-keys
```

Verify installation:
```bash
project-context-server --version
# or just: which project-context-server
```

---

### Step 2 — Configure your MCP client

Add the server to Claude Desktop's config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

**With Ollama:**
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

**With Voyage AI:**
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

Restart Claude Desktop after saving the config.

---

### Step 3 — Index your project

In Claude Desktop, start a new conversation and ask:

> "Index the project at `/path/to/my-project`."

Claude will call `index_project_context`. Indexing a typical project takes 10–120 seconds depending on size and embedding provider speed. The index is persisted to `~/.mcp-project-context/chroma` and only needs to be rebuilt when files change significantly.

---

### Step 4 — Start working

You can now ask Claude natural questions about your codebase:

> "How does authentication work in this project?"
> "Find all places where database connections are created."
> "What does the `UserService` class do?"

On subsequent conversations, the index is already built — queries run immediately.

**Re-indexing:** Ask Claude to re-index whenever you've made major changes:
> "Re-index `/path/to/my-project` — I've refactored the auth module."

---

### Topology 1 summary

```
Developer laptop
├── Claude Desktop (MCP client)
│   └── spawns: project-context-server (STDIO subprocess)
│         ├── EMBED_PROVIDER=ollama → localhost:11434
│         ├── VECTOR_STORE_PROVIDER=chroma-local → ~/.mcp-project-context/chroma/
│         └── REPO_PROVIDER=local → /path/to/project/
└── Ollama server (ollama serve)
```

---

---

## Topology 2: Team Server

**Stack:** HTTP/SSE + `github` repo provider + `pgvector` vector store + bearer token auth

One server instance is shared across a team. Embeddings are stored in a shared PostgreSQL+pgvector database, so all team members query the same pre-built index. The server connects to GitHub to fetch repositories.

---

### Step 1 — Prerequisites

**PostgreSQL with pgvector:**
```bash
# Docker Compose example for local/dev server:
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: mcpuser
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: mcp_context
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
EOF
docker compose up -d

# Initialize the pgvector extension
psql postgresql://mcpuser:changeme@localhost:5432/mcp_context \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

For production, use a managed PostgreSQL service (AWS RDS, Google Cloud SQL, Azure Database for PostgreSQL, Supabase, etc.) and follow their pgvector setup guides.

**GitHub Personal Access Token:**
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Create a token with `repo` scope (or `public_repo` if only indexing public repos)
3. Note the token value — you'll only see it once

**Generate a bearer token for MCP auth:**
```bash
openssl rand -hex 32
# Example output: a3f8d2...c9b1e4  (64 hex characters)
# Save this as MCP_AUTH_TOKEN
```

---

### Step 2 — Install with extras

On the server machine:

```bash
pip install "mcp-project-context-server[voyage,pgvector,sse]"
# or with OpenAI embeddings:
pip install "mcp-project-context-server[openai,pgvector,sse]"
```

---

### Step 3 — Set environment variables

Create an environment file (e.g., `/etc/mcp-context-server.env`):

```bash
# Transport
MCP_TRANSPORT=sse
MCP_HOST=0.0.0.0
MCP_PORT=8080
MCP_AUTH_TYPE=bearer
MCP_AUTH_TOKEN=a3f8d2...c9b1e4   # from Step 1

# Embeddings — Voyage AI (recommended for code)
EMBED_PROVIDER=voyage
VOYAGE_API_KEY=pa-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
VOYAGE_EMBED_MODEL=voyage-code-3

# Vector store — pgvector
VECTOR_STORE_PROVIDER=pgvector
PGVECTOR_CONNECTION_STRING=postgresql://mcpuser:changeme@localhost:5432/mcp_context

# Repository — GitHub
REPO_PROVIDER=github
GITHUB_TOKEN=ghp_xx...xxxx
```

> **Security:** Restrict permissions on the env file: `chmod 600 /etc/mcp-context-server.env`

---

### Step 4 — Run the server

**Direct (testing/development):**
```bash
source /etc/mcp-context-server.env
project-context-server
# Server starts on 0.0.0.0:8080
```

**systemd service (production):**
```ini
# /etc/systemd/system/mcp-context-server.service
[Unit]
Description=MCP Project Context Server
After=network.target postgresql.service

[Service]
Type=simple
User=mcp
EnvironmentFile=/etc/mcp-context-server.env
ExecStart=/usr/local/bin/project-context-server
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now mcp-context-server
systemctl status mcp-context-server
```

**Docker:**
```bash
docker run -d \
  --name mcp-context-server \
  --env-file /etc/mcp-context-server.env \
  -p 8080:8080 \
  --restart unless-stopped \
  python:3.11-slim \
  sh -c "pip install 'mcp-project-context-server[voyage,pgvector,sse]' && project-context-server"
```

---

### Step 5 — Configure Cursor for each team member

Each developer adds or commits `.cursor/mcp.json` to the project repo:

```json
{
  "mcpServers": {
    "project-context": {
      "url": "https://mcp.internal.example.com/sse",
      "headers": {
        "Authorization": "Bearer a3f8d2...c9b1e4"
      }
    }
  }
}
```

Replace `mcp.internal.example.com` with your server's hostname or IP.

Team members using Claude Desktop add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "project-context": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sse-client",
               "https://mcp.internal.example.com/sse"],
      "env": {
        "MCP_AUTH_HEADER": "Authorization: Bearer a3f8d2...c9b1e4"
      }
    }
  }
}
```

> Alternatively, individual team members can run their own local STDIO instances pointing at the shared pgvector database.

---

### Step 6 — Pre-index team repositories

An admin (or CI job) indexes the repos once so the index is ready for everyone:

```bash
# Using curl to call index_project_context via the SSE endpoint
curl -X POST \
  -H "Authorization: Bearer a3f8d2...c9b1e4" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "index_project_context",
      "arguments": {
        "project_path": "acme/backend"
      }
    }
  }' \
  https://mcp.internal.example.com/mcp
```

Or ask any MCP-connected client (Claude Desktop, Cursor) to index the repos:
> "Index the `acme/backend` GitHub repository."

---

### Topology 2 summary

```
Team server (VM / container)
├── project-context-server (SSE on :8080, bearer auth)
│   ├── EMBED_PROVIDER=voyage
│   ├── VECTOR_STORE_PROVIDER=pgvector → PostgreSQL:5432
│   └── REPO_PROVIDER=github → api.github.com
│
Developer laptops (clients)
├── Cursor → .cursor/mcp.json → https://mcp.internal:8080/sse
├── Claude Desktop → claude_desktop_config.json → same
└── GitHub Copilot → .vscode/mcp.json → same
```

---

---

## Topology 3: Enterprise / Agent Engine

**Stack:** HTTP/SSE + Google IAM auth + `github` multi-tenant + `pgvector` (Cloud SQL) + `google-vertex` embeddings

A single Cloud Run service handles embedding and retrieval for an entire organization. Vertex AI Agent Engine calls it with Google-signed OIDC tokens. Multiple GitHub organizations are supported from one deployment.

---

### Step 1 — Prerequisites

- GCP project with these APIs enabled:
  ```bash
  gcloud services enable \
    run.googleapis.com \
    aiplatform.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com
  ```
- Cloud SQL (PostgreSQL 16) instance with pgvector:
  ```bash
  gcloud sql instances create mcp-pg \
    --database-version=POSTGRES_16 \
    --tier=db-g1-small \
    --region=us-central1

  gcloud sql databases create mcp_context --instance=mcp-pg

  gcloud sql users create mcpuser \
    --instance=mcp-pg \
    --password=<strong-password>
  ```
  Then connect and run: `CREATE EXTENSION IF NOT EXISTS vector;`

- Two service accounts:
  ```bash
  # Service account for the Cloud Run service (mcp-server-sa)
  gcloud iam service-accounts create mcp-server-sa \
    --display-name "MCP Context Server"

  # Service account for Agent Engine to use when calling Cloud Run (agent-engine-sa)
  gcloud iam service-accounts create agent-engine-sa \
    --display-name "Agent Engine Caller"
  ```

- GitHub token (or GitHub App) with `repo` scope for the organizations you want to index
- Store secrets in Secret Manager:
  ```bash
  echo -n "ghp_xx...xxxx" | \
    gcloud secrets create github-token --data-file=-

  echo -n "postgresql://mcpuser:<pw>@/mcp_context?host=/cloudsql/PROJECT:us-central1:mcp-pg" | \
    gcloud secrets create pgvector-conn-string --data-file=-
  ```

---

### Step 2 — Build and deploy to Cloud Run

**Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir "mcp-project-context-server[google-vertex,pgvector,sse]"
EXPOSE 8080
CMD ["project-context-server"]
```

```bash
# Build and push
gcloud builds submit --tag gcr.io/MY_PROJECT/mcp-context-server:latest

# Deploy
gcloud run deploy mcp-context-server \
  --image gcr.io/MY_PROJECT/mcp-context-server:latest \
  --region us-central1 \
  --service-account mcp-server-sa@MY_PROJECT.iam.gserviceaccount.com \
  --no-allow-unauthenticated \
  --port 8080 \
  --set-env-vars "MCP_TRANSPORT=sse" \
  --set-env-vars "MCP_AUTH_TYPE=google-iam" \
  --set-env-vars "EMBED_PROVIDER=google-vertex" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=MY_PROJECT" \
  --set-env-vars "GOOGLE_CLOUD_LOCATION=us-central1" \
  --set-env-vars "VERTEX_EMBED_MODEL=text-embedding-005" \
  --set-env-vars "VECTOR_STORE_PROVIDER=pgvector" \
  --set-env-vars "REPO_PROVIDER=github" \
  --set-env-vars "REPO_MULTI_TENANT=true" \
  --set-env-vars "APPROVED_ORGS=acme,acme-labs" \
  --set-secrets "GITHUB_TOKEN=github-token:latest" \
  --set-secrets "PGVECTOR_CONNECTION_STRING=pgvector-conn-string:latest" \
  --add-cloudsql-instances MY_PROJECT:us-central1:mcp-pg

# Get the service URL
SERVICE_URL=$(gcloud run services describe mcp-context-server \
  --region us-central1 --format 'value(status.url)')
echo "Service URL: $SERVICE_URL"
```

---

### Step 3 — Set `GOOGLE_IAM_AUDIENCE` and configure IAM

Update the deployment with the service URL (required for OIDC token validation):

```bash
gcloud run services update mcp-context-server \
  --region us-central1 \
  --update-env-vars "GOOGLE_IAM_AUDIENCE=$SERVICE_URL" \
  --update-env-vars "GOOGLE_APPROVED_SERVICE_ACCOUNTS=agent-engine-sa@MY_PROJECT.iam.gserviceaccount.com"
```

Grant Agent Engine's service account permission to call Cloud Run:
```bash
gcloud run services add-iam-policy-binding mcp-context-server \
  --region us-central1 \
  --member "serviceAccount:agent-engine-sa@MY_PROJECT.iam.gserviceaccount.com" \
  --role roles/run.invoker
```

Grant the Cloud Run service account access to Vertex AI and Secret Manager:
```bash
gcloud projects add-iam-policy-binding MY_PROJECT \
  --member "serviceAccount:mcp-server-sa@MY_PROJECT.iam.gserviceaccount.com" \
  --role roles/aiplatform.user

gcloud projects add-iam-policy-binding MY_PROJECT \
  --member "serviceAccount:mcp-server-sa@MY_PROJECT.iam.gserviceaccount.com" \
  --role roles/secretmanager.secretAccessor

gcloud projects add-iam-policy-binding MY_PROJECT \
  --member "serviceAccount:mcp-server-sa@MY_PROJECT.iam.gserviceaccount.com" \
  --role roles/cloudsql.client
```

---

### Step 4 — Configure Agent Engine

In your Agent Engine agent definition (Python SDK example):

```python
import vertexai
from vertexai.preview.reasoning_engines import LangchainAgent

vertexai.init(project="MY_PROJECT", location="us-central1")

agent = LangchainAgent(
    model="gemini-2.0-flash-001",
    tools=[
        {
            "type": "mcp",
            "server_url": "https://mcp-context-HASH-uc.a.run.app",
            "auth": {
                "type": "google_iam",
                "service_account_email": "agent-engine-sa@MY_PROJECT.iam.gserviceaccount.com",
                "audience": "https://mcp-context-HASH-uc.a.run.app"
            }
        }
    ],
    system_instruction="""You are a code assistant with access to a project context server.
    Use list_repositories to discover available repositories.
    Use index_project_context before searching a repository for the first time.
    Use search_project_context to find relevant code when answering questions."""
)
```

> Consult the [Agent Engine documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) for the precise API — the configuration structure varies by agent framework and SDK version.

---

### Step 5 — Use `list_repositories` for multi-tenant repo discovery

With `REPO_MULTI_TENANT=true`, the server exposes a `list_repositories` tool. Agents use this to discover which repositories are available before indexing or searching.

**Example agent prompt that leverages multi-tenant discovery:**
```
Use list_repositories to show me all available repositories in the acme org.
Then index the backend service and explain how it handles payment processing.
```

The agent will:
1. Call `list_repositories` → receives list filtered by `APPROVED_ORGS=acme,acme-labs`
2. Choose `acme/backend`
3. Call `index_project_context(project_path="acme/backend")` 
4. Call `search_project_context(project_path="acme/backend", query="payment processing")`
5. Return an answer grounded in the actual code

---

### Topology 3 summary

```
GCP Project: MY_PROJECT
│
├── Agent Engine (Vertex AI)
│   └── uses service account: agent-engine-sa
│       └── calls (OIDC) ──►
│
├── Cloud Run: mcp-context-server
│   ├── service account: mcp-server-sa
│   ├── MCP_AUTH_TYPE=google-iam
│   ├── REPO_MULTI_TENANT=true, APPROVED_ORGS=acme,acme-labs
│   ├── EMBED_PROVIDER=google-vertex ──► Vertex AI
│   └── VECTOR_STORE_PROVIDER=pgvector ──►
│
├── Cloud SQL: mcp-pg (PostgreSQL 16 + pgvector)
│
└── External: GitHub (api.github.com) ◄── GITHUB_TOKEN (Secret Manager)
```

---

## Choosing the Right Topology

| Question | Answer | Use |
|---|---|---|
| Am I the only user? | Yes | Topology 1 |
| Do I want free/offline embeddings? | Yes | Topology 1 (Ollama) |
| Do I want the best retrieval quality locally? | Yes | Topology 1 (Voyage) |
| Am I setting up for a small team (2–20 people)? | Yes | Topology 2 |
| Is my team on GCP / using Gemini models? | Yes | Topology 3 |
| Do I need multi-org repo governance? | Yes | Topology 3 |
| Do I need autonomous agents to discover and index repos? | Yes | Topology 3 |
