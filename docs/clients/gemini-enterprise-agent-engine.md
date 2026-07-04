# Gemini Enterprise — Agent Engine

## Overview

[Google Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) (formerly Reasoning Engine) is a managed runtime for deploying AI agents on Google Cloud. In this topology, `mcp-project-context-server` runs as a **long-lived HTTP/SSE service** (typically on Cloud Run) and Agent Engine calls it over the network using **Google IAM OIDC authentication**. A single server deployment can serve your entire organization in **multi-tenant mode**, serving multiple GitHub organizations and repositories from one endpoint.

> **What this server does:** `mcp-project-context-server` indexes and searches the `.context/` directory of a project — `project.md`, ADRs under `.context/decisions/`, and session notes under `.context/sessions/`. It does not index or search your general source code.
>
> **Repository provider caveat for this topology:** with `REPO_PROVIDER=github` and `REPO_MULTI_TENANT=true`, the `list_repositories` tool discovers repositories over the GitHub REST API — no local checkout needed for discovery. However, `load_project_context`, `index_project_context`, `search_project_context`, and `save_session_summary` still read and write `.context/` on the filesystem of the Cloud Run container itself, not via the GitHub API. For those four tools to work in this deployment, the target repository's `.context/` directory must already be present on disk inside the container (e.g. baked into the image, or synced by an init step) at the path passed as `project_path`.

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

`REPO_MULTI_TENANT=true` requires at least one of `APPROVED_ORGS` or `APPROVED_REPOS` to be set (the server fails at startup otherwise) and makes that allowlist available to `list_repositories`, which is registered on every deployment regardless of this setting.

### `list_repositories`

Agents can call this tool to discover which GitHub repositories are available (via the GitHub REST API) before deciding which ones to work with. Results are filtered to the `APPROVED_ORGS` / `APPROVED_REPOS` allowlist.

**Agent prompt example:**

```
Use list_repositories to find all available repositories in the acme org.
```

> **Note on the other tools:** `list_repositories` is the only tool that currently reads through the GitHub REST API. `load_project_context`, `index_project_context`, `search_project_context`, and `save_session_summary` read/write `.context/` on the server's local filesystem and do not check the discovered repository against the `APPROVED_ORGS` / `APPROVED_REPOS` allowlist — plan your deployment (e.g. which `.context/` directories are mounted into the container) accordingly rather than relying on the allowlist to restrict what these four tools can access.

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
| `GOOGLE_IAM_AUDIENCE` | _(none)_ | Expected `aud` claim in Google identity tokens. If unset, audience validation is skipped |
| `GOOGLE_APPROVED_SERVICE_ACCOUNTS` | _(none)_ | Comma-separated allowed caller service account emails. If unset, any authenticated Google identity is accepted |

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

Confirm the SSE endpoint accepts the token (the connection stays open for a live MCP session, so this just checks that it's reachable and doesn't immediately reject the token):

```bash
curl -N -H "Authorization: Bearer $TOKEN" \
  https://mcp-context-HASH-uc.a.run.app/sse
```

MCP JSON-RPC calls (`tools/list`, `tools/call`, etc.) are exchanged over this SSE session and a paired `/messages/` POST endpoint — there is no single-shot HTTP endpoint for `tools/list`. To exercise the full protocol, connect with a real MCP client (e.g. an `mcp` Python/TypeScript SDK client, or Agent Engine itself) configured with the `server_url` and bearer token shown above, and confirm it lists `index_project_context`, `search_project_context`, `load_project_context`, `save_session_summary`, and `list_repositories`.
