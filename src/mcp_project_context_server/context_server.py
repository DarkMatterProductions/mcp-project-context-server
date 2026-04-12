"""
Project Context MCP Server
Serves .context/ directory files to an LLM via the Model Context Protocol.
Supports semantic search via ChromaDB + Ollama nomic-embed-text.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

import chromadb
from chromadb.config import Settings
import ollama
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# ── Configuration ──────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# Build CHROMA_DIR from env var if set, otherwise use a platform-correct default.
# Path() normalises separators on both Windows and Linux automatically.
_chroma_default: Path = Path.home() / ".mcp-data" / "chroma"
CHROMA_DIR: Path = Path(os.getenv("CHROMA_DIR", str(_chroma_default)))
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ── ChromaDB setup ─────────────────────────────────────────────────────────────
# chromadb.PersistentClient requires a str — this is the only place we
# explicitly convert a Path to str, at the external API boundary.
chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR),
    settings=Settings(anonymized_telemetry=False)
)

# ── Ollama embedding helper ────────────────────────────────────────────────────
def get_embedding(text: str) -> list[float]:
    """Generate an embedding for text using Ollama."""
    client = ollama.Client(host=OLLAMA_BASE_URL)
    response = client.embeddings(model=EMBED_MODEL, prompt=text)
    return response["embedding"]

# ── Context file helpers ───────────────────────────────────────────────────────
def find_context_dir(project_path: str | Path) -> Path | None:
    """Walk up from project_path to find a .context/ directory."""
    p = Path(project_path).resolve()
    for candidate in [p, *p.parents]:
        ctx = candidate / ".context"
        if ctx.is_dir():
            return ctx
    return None

def collection_name_for(context_dir: Path) -> str:
    """Derive a stable ChromaDB collection name from the project root directory.

    Always based on context_dir.parent so it's consistent regardless of
    whether the caller passed a project root, a subdirectory, or a file path.
    """
    project_name = context_dir.parent.name
    return f"ctx_{project_name}".replace("-", "_").replace(" ", "_")[:63]

def read_context_files(context_dir: Path) -> dict[str, str]:
    """Read all markdown files from .context/ into a dict.

    Keys use POSIX-style forward slashes (via Path.as_posix()) so that
    ChromaDB document IDs and metadata are identical on Windows and Linux.
    """
    return {
        md_file.relative_to(context_dir).as_posix(): md_file.read_text(encoding="utf-8")
        for md_file in context_dir.rglob("*.md")
    }

def index_project_context(project_path: str | Path) -> str:
    """Index .context/ files into ChromaDB for semantic search."""
    context_dir = find_context_dir(project_path)
    if not context_dir:
        return f"No .context/ directory found at or above {project_path}"

    col_name = collection_name_for(context_dir)

    # Drop and recreate the collection for a clean re-index
    try:
        chroma_client.delete_collection(col_name)
    except Exception:
        pass
    collection = chroma_client.create_collection(col_name)

    files = read_context_files(context_dir)
    indexed = 0

    for filename, content in files.items():
        # Chunk large files (e.g., BUNDLE.md) into 1000-char segments
        chunks = [content[i:i + 1000] for i in range(0, len(content), 1000)]
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            doc_id = f"{filename}::{i}"
            try:
                embedding = get_embedding(chunk)
                collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"file": filename, "chunk": i}]
                )
                indexed += 1
            except Exception as e:
                print(f"Warning: failed to index {doc_id}: {e}", file=sys.stderr)

    return f"Indexed {indexed} chunks from {len(files)} files into collection '{col_name}'"

# ── MCP Server ─────────────────────────────────────────────────────────────────
server = Server("project-context")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="load_project_context",
            description=(
                "Load the full project context for the given project path. "
                "Returns project.md, all ADRs, and the latest session summary. "
                "Call this at the start of every session."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Absolute path to the project root or any file within it."
                    }
                },
                "required": ["project_path"]
            }
        ),
        types.Tool(
            name="search_project_context",
            description=(
                "Semantically search the indexed project context. "
                "Use this to find relevant past decisions, architecture notes, "
                "or code summaries related to your current task."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"},
                    "query": {"type": "string", "description": "Natural language search query"},
                    "n_results": {"type": "integer", "default": 5}
                },
                "required": ["project_path", "query"]
            }
        ),
        types.Tool(
            name="save_session_summary",
            description=(
                "Save a summary of the current session to .context/sessions/YYYY-MM-DD.md. "
                "Call this at the end of a session with a concise summary of what was done."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"},
                    "summary": {
                        "type": "string",
                        "description": "Markdown summary: what was worked on, decisions made, next steps."
                    }
                },
                "required": ["project_path", "summary"]
            }
        ),
        types.Tool(
            name="index_project_context",
            description=(
                "Re-index the .context/ directory into the vector store. "
                "Run this after updating project.md, adding ADRs, or refreshing BUNDLE.md."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"}
                },
                "required": ["project_path"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:

    if name == "load_project_context":
        context_dir = find_context_dir(arguments["project_path"])
        if not context_dir:
            return [types.TextContent(type="text", text=f"No .context/ directory found near {arguments['project_path']}")]

        parts = []

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

    elif name == "search_project_context":
        query = arguments["query"]
        n_results = arguments.get("n_results", 5)

        # Always resolve the collection name via find_context_dir so that a
        # file path, subdirectory, or project root all map to the same collection.
        context_dir = find_context_dir(arguments["project_path"])
        if not context_dir:
            return [types.TextContent(type="text", text=f"No .context/ directory found near {arguments['project_path']}")]

        col_name = collection_name_for(context_dir)

        try:
            collection = chroma_client.get_collection(col_name)
        except Exception:
            return [types.TextContent(
                type="text",
                text=f"Collection '{col_name}' not found. Run index_project_context first."
            )]

        query_embedding = get_embedding(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count())
        )

        if not results["documents"][0]:
            return [types.TextContent(type="text", text="No results found.")]

        output_parts = [
            f"**[{meta['file']}]**\n{doc}"
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]
        return [types.TextContent(type="text", text="\n\n---\n\n".join(output_parts))]

    elif name == "save_session_summary":
        summary = arguments["summary"]
        context_dir = find_context_dir(arguments["project_path"])
        if not context_dir:
            return [types.TextContent(type="text", text=f"No .context/ directory found near {arguments['project_path']}")]

        sessions_dir = context_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        session_file = sessions_dir / f"{today}.md"

        if session_file.exists():
            timestamp = datetime.now().strftime("%H:%M")
            content = f"{session_file.read_text(encoding='utf-8')}\n\n### Session at {timestamp}\n\n{summary}"
        else:
            content = f"# Session: {today}\n\n{summary}"

        session_file.write_text(content, encoding="utf-8")
        # as_posix() gives a consistent forward-slash path in the confirmation
        # message regardless of platform.
        return [types.TextContent(type="text", text=f"Session summary saved to {session_file.as_posix()}")]

    elif name == "index_project_context":
        result = index_project_context(arguments["project_path"])
        return [types.TextContent(type="text", text=result)]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

# ── Entry point ────────────────────────────────────────────────────────────────
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())