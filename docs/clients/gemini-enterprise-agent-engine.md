# Gemini Enterprise — Agent Engine

## Overview

[Google Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) (formerly Reasoning Engine) is a managed runtime for deploying AI agents on Google Cloud. In this topology, `mcp-project-context-server` runs as a **long-lived HTTP/SSE service** (typically on Cloud Run) and Agent Engine calls it over the network using **Google IAM OIDC authentication**. A single server deployment can serve your entire organization in **multi-tenant mode**, serving multiple GitHub organizations and repositories from one endpoint.

---

## Architecture

```
Agent Engine (Vertex AI)
   └─ calls ──► Cloud Run: mcp-project-context-server
                  ├─ EMBED_PROVIDER=vertexai
                  ├─ VECTOR_STORE_PROVIDER=pgvector  ──► Cloud SQL (PostgreSQL + pgvector)
                  ├─ REPO_PROVIDER=github
                  └─ REPO_MULTI_TENANT=true
```

---

## Prerequisites

- A GCP project with the following APIs enabled:
  - Vertex AI API (`aiplatform.googleapis.com`)
  - Cloud Run API (`run.googleapis.com`)
  - Cloud SQL Admin API (if using Cloud SQL)
  - Secret Manager API (recommended for storing tokens)
- A service account for the Cloud Run service
- A service account for Agent Engine to use when calling Cloud Run
- PostgreSQL (Cloud SQL) instance with the `pgvector` extension
- GitHub Personal Access Token or GitHub App private key

---

## Installation

For Cloud Run deployment, use the `[google-vertex,pgvector,sse]` extras:

```bash
pip install "mcp-project-context-server[google-vertex,pgvector,sse]"
```

Or in your `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN pip install "mcp-project-context-server[google-vertex,pgvector,sse]"

CMD ["project-context-server"]
```

---

## Configuration

### Environment Variables

Set these on your Cloud Run service:

```bash
# Transport
MCP_TRANSPORT=sse
MCP_HOST=0.0.0.0
MCP_PORT=8080
MCP_AUTH_TYPE=google-iam

# Google IAM Auth
GOOGLE_IAM_AUDIENCE=https://mcp-context-HASH-uc.a.run.app
# List the Agent Engine service account(s) allowed to call this service:
GOOGLE_APPROVED_SERVICE_ACCOUNTS=agent-engine-sa@my-gcp-project.iam.gserviceaccount.com

# Embedding — Vertex AI (recommended; uses Cloud Run service account via Workload Identity)
EMBED_PROVIDER=vertexai
VERTEXAI_PROJECT=my-gcp-project
VERTEXAI_LOCATION=us-central1
VERTEXAI_EMBED_MODEL=text-embedding-004

# Vector Store — pgvector on Cloud SQL
VECTOR_STORE_PROVIDER=pgvector
PGVECTOR_CONNECTION_STRING=postgresql://mcpuser:***@/mcp_context?host=/cloudsql/my-gcp-project:us-central1:my-pg-instance

# Repository — GitHub multi-tenant
REPO_PROVIDER=github
REPO_AUTH_TOKEN=ghp_xx...xxxx
REPO_MULTI_TENANT=true
APPROVED_ORGS=acme,acme-labs
# Optionally restrict to specific repos:
# APPROVED_REPOS=acme/backend,acme/frontend
```

> **Security best practice:** Store `REPO_AUTH_TOKEN` and `PGVECTOR_CONNECTION_STRING` in [Secret Manager](https://cloud.google.com/secret-manager) and mount them as environment variables in Cloud Run using the `--set-secrets` flag.

---

### Cloud Run Deployment

```bash
gcloud run deploy mcp-context-server \
  --image gcr.io/my-gcp-project/mcp-context-server:latest \
  --region us-central1 \
  --service-account mcp-server-sa@my-gcp-project.iam.gserviceaccount.com \
  --no-allow-unauthenticated \
  --set-env-vars MCP_TRANSPORT=sse,MCP_AUTH_TYPE=google-iam \
  --set-env-vars GOOGLE_IAM_AUDIENCE=https://mcp-context-HASH-uc.a.run.app \
  --set-env-vars EMBED_PROVIDER=vertexai,VERTEXAI_PROJECT=my-gcp-project,VERTEXAI_LOCATION=us-central1 \
  --set-env-vars VECTOR_STORE_PROVIDER=pgvector \
  --set-env-vars REPO_PROVIDER=github,REPO_MULTI_TENANT=true \
  --set-env-vars APPROVED_ORGS=acme,acme-labs \
  --set-secrets REPO_AUTH_TOKEN=github-token:latest \
  --set-secrets PGVECTOR_CONNECTION_STRING=pgvector-conn-string:latest \
  --add-cloudsql-instances my-gcp-project:us-central1:my-pg-instance \
  --port 8080
```

After deploying, capture the service URL:

```bash
SERVICE_URL=$(gcloud run services describe mcp-context-server \
  --region us-central1 \
  --format 'value(status.url)')
echo $SERVICE_URL
# https://mcp-context-HASH-uc.a.run.app
```

Update `GOOGLE_IAM_AUDIENCE` to match this URL exactly.

---

### IAM Permissions

Grant the Agent Engine service account permission to invoke the Cloud Run service:

```bash
gcloud run services add-iam-policy-binding mcp-context-server \
  --region us-central1 \
  --member serviceAccount:agent-engine-sa@my-gcp-project.iam.gserviceaccount.com \
  --role roles/run.invoker
```

Grant the Cloud Run service account permission to use Vertex AI embeddings:

```bash
gcloud projects add-iam-policy-binding my-gcp-project \
  --member serviceAccount:mcp-server-sa@my-gcp-project.iam.gserviceaccount.com \
  --role roles/aiplatform.user
```

---

### Google IAM Auth Setup

When `MCP_AUTH_TYPE=google-iam`, every incoming HTTP request must carry a Google-signed OIDC ID token in the `Authorization: Bearer` header. Agent Engine automatically attaches these tokens when configured correctly.

The server validates:
1. The token is a valid Google-signed OIDC token
2. The `aud` claim matches `GOOGLE_IAM_AUDIENCE`
3. The `email` claim (service account) is in `GOOGLE_APPROVED_SERVICE_ACCOUNTS` (if set)

---

### Agent Engine Configuration

In your Agent Engine (Vertex AI) agent definition, configure the MCP tool endpoint:

```python
from vertexai.preview.reasoning_engines import LangchainAgent
# or your agent framework of choice

agent = LangchainAgent(
    model="gemini-2.0-flash",
    tools=[
        {
            "type": "mcp",
            "server_url": "https://mcp-context-HASH-uc.a.run.app",
            "auth": {
                "type": "google_iam",
                "service_account": "agent-engine-sa@my-gcp-project.iam.gserviceaccount.com",
                "audience": "https://mcp-context-HASH-uc.a.run.app"
            }
        }
    ]
)
```

> Refer to the [Agent Engine documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) for the exact API, as the configuration format depends on your agent framework and SDK version.

---

## Multi-Tenant Mode

With `REPO_MULTI_TENANT=true`, the server exposes a `list_repositories` tool in addition to the standard indexing and search tools.

### `list_repositories`

Agents can call this tool to discover which repositories are available before deciding which ones to index or query.

**Agent prompt example:**

```
Use list_repositories to find all available repositories in the acme org,
then index and search the backend service for how authentication is implemented.
```

The tool returns repositories filtered by `APPROVED_ORGS` and `APPROVED_REPOS`. This prevents agents from accessing repositories outside the approved set, even if the auth token has broader access.

---

## Vector Store — pgvector

pgvector on Cloud SQL is the recommended vector store for Agent Engine deployments:

- **Durability:** Indexes persist across Cloud Run instance restarts and scaling events
- **Shared access:** Multiple Cloud Run instances (scale-out) read from the same index
- **No re-indexing on cold start:** Agents can query immediately after a new deployment

Initialize the schema before first use:

```sql
-- Connect to the database and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

The server creates the embeddings table automatically on first run.

---

## Embedding Provider — Vertex AI

`EMBED_PROVIDER=vertexai` is recommended for Agent Engine deployments because:

- Authentication uses [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) / the Cloud Run service account — no API key management
- Embeddings are generated within GCP's network — lower latency and no egress charges

**Environment variables:**

| Variable | Default | Required |
|----------|---------|----------|
| `EMBED_PROVIDER` | — | **Yes** (`vertexai`) |
| `VERTEXAI_PROJECT` | — | **Yes** |
| `VERTEXAI_LOCATION` | — | **Yes** |
| `VERTEXAI_EMBED_MODEL` | `text-embedding-004` | No |

---

## SSE Transport Environment Variables

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

## Verification / Quick Test

Test the Cloud Run service health from a local machine (requires the `cloud-run-invoker` role on your user account):

```bash
TOKEN=$(gcloud auth print-identity-token \
  --audiences https://mcp-context-HASH-uc.a.run.app)

curl -H "Authorization: Bearer $TOKEN" \
  https://mcp-context-HASH-uc.a.run.app/health
# Expected: {"status": "ok"}
```

Test a full MCP call:

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  https://mcp-context-HASH-uc.a.run.app/mcp
```

This should return a list of available tools including `index_project_context`, `search_project_context`, and (in multi-tenant mode) `list_repositories`.
