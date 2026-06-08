"""MCP server setup, tool registry, and entry point.

Transport selection
-------------------
Set ``MCP_TRANSPORT`` to choose the transport:

``stdio`` *(default)*
    Standard input/output.  Used by Claude Desktop, Claude Code, Cursor,
    JetBrains AI Assistant, Continue Dev, and GitHub Copilot.

``sse``
    HTTP/SSE.  Used for remote deployments, team servers, and Gemini
    Enterprise Agent Engine.  See ``transport/sse.py`` for auth configuration.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from mcp import types
from mcp.server import Server

from mcp_project_context_server.tools import (
    index_context,
    list_repositories,
    load_context,
    save_session,
    search_context,
)

_LOG_PATH = Path.home() / ".mcp-data" / "logs" / "project-context-server.log"
_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=_LOG_PATH,
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


server = Server("project-context")

_TOOL_DEFINITIONS: list[types.Tool] = [
    types.Tool(
        name="load_project_context",
        description=(
            "Load the full project context for the given project path. "
            "Returns project.md, all ADRs, and the latest session summary. "
            "You MUST call this at the start of every session."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": (
                        "Absolute filesystem path, a short 'owner/repo' identifier, "
                        "or a full https:// repository URL."
                    ),
                }
            },
            "required": ["project_path"],
        },
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
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
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
                    "description": "Markdown summary: what was worked on, decisions made, next steps.",
                },
            },
            "required": ["project_path", "summary"],
        },
    ),
    types.Tool(
        name="index_project_context",
        description=(
            "Re-index the .context/ directory into the vector store. "
            "Run this after updating project.md, adding ADRs, or refreshing BUNDLE.md."
        ),
        inputSchema={
            "type": "object",
            "properties": {"project_path": {"type": "string"}},
            "required": ["project_path"],
        },
    ),
    types.Tool(
        name="list_repositories",
        description=(
            "List repositories accessible via the configured repository provider. "
            "In multi-tenant deployments, use this to discover which repositories are "
            "available before calling other tools.  Optionally filter by organisation name."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "org": {
                    "type": "string",
                    "description": "Optional: filter results to repositories in this organisation.",
                }
            },
            "required": [],
        },
    ),
]

_TOOL_HANDLERS = {
    "load_project_context": load_context.handle,
    "search_project_context": search_context.handle,
    "save_session_summary": save_session.handle,
    "index_project_context": index_context.handle,
    "list_repositories": list_repositories.handle,
}


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return _TOOL_DEFINITIONS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    handler = _TOOL_HANDLERS.get(name)
    if not handler:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    return await handler(arguments)


async def _main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport == "stdio":
        from mcp_project_context_server.transport.stdio import run_stdio

        await run_stdio(server)

    elif transport == "sse":
        from mcp_project_context_server.transport.sse import run_sse

        await run_sse(server)

    else:
        raise EnvironmentError(f"Unsupported MCP_TRANSPORT value '{transport}'.  " "Supported values are: stdio, sse")


def run() -> None:
    logger.info("project-context-server starting")
    try:
        asyncio.run(_main())
    except Exception:
        logger.exception("Server crashed at top level")
        raise
