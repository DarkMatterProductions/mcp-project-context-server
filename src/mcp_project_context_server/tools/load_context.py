"""Tool: load_project_context — loads project.md, ADRs, and last session."""

import importlib.metadata
import os

from mcp import types

from mcp_project_context_server.helpers.context import collection_name_for, find_context_dir
from mcp_project_context_server.integrations.chroma.client import chroma_client

_MIGRATION_NOTICE = (
    "⚠️ **Re-index required**: This project's search index was built with an older "
    "version of `mcp-project-context-server`. Run `index_project_context` to rebuild "
    "with the new heading-boundary chunking strategy and restore full retrieval precision."
)

try:
    _SERVER_VERSION: str = importlib.metadata.version("mcp-project-context-server")
except importlib.metadata.PackageNotFoundError:
    _SERVER_VERSION = "unknown"


def _needs_reindex(context_dir) -> bool:
    """Return True if the ChromaDB collection exists but was built with a different server version."""
    col_name = collection_name_for(context_dir)
    try:
        collection = chroma_client.get_collection(col_name)
        collection_version = (collection.metadata or {}).get("server_version")
        # If no server_version field the collection pre-dates this feature — needs re-index.
        return collection_version != _SERVER_VERSION
    except Exception:
        # Collection does not exist yet — nothing to warn about.
        return False


async def handle(arguments: dict) -> list[types.TextContent]:
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    context_dir = find_context_dir(_project_path)
    if not context_dir:
        return [
            types.TextContent(
                type="text",
                text=f"No .context/ directory found near {arguments['project_path']}",
            )
        ]

    parts: list[str] = []

    # Migration notice — prepended when the indexed collection is stale
    if _needs_reindex(context_dir):
        parts.append(_MIGRATION_NOTICE)

    project_md = context_dir / "project.md"
    if project_md.exists():
        parts.append(f"## project.md\n\n{project_md.read_text(encoding='utf-8')}")

    decisions_dir = context_dir / "decisions"
    if decisions_dir.exists():
        adrs = sorted(decisions_dir.glob("*.md"))
        if adrs:
            parts.append("## Architecture Decisions\n")
            for adr in adrs:
                parts.append(f"### {adr.name}\n{adr.read_text(encoding='utf-8')}")

    sessions_dir = context_dir / "sessions"
    if sessions_dir.exists():
        session_files = sorted(sessions_dir.glob("*.md"))
        if session_files:
            latest = session_files[-1]
            parts.append(f"## Last Session ({latest.stem})\n\n{latest.read_text(encoding='utf-8')}")

    result = "\n\n---\n\n".join(parts)
    return [types.TextContent(type="text", text=result or "No context files found.")]
