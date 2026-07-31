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
from typing import Any

from mcp import types
from mcp.server import Server
from mcp.types import CallToolResult, TextContent

from mcp_project_context_server.tools import (
    index_context,
    list_repositories,
    load_context,
    save_session,
    search_context,
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
    """List the MCP tools exposed by this server.

    :return: (list) The registered ``types.Tool`` definitions advertised to MCP clients.
    """
    return _TOOL_DEFINITIONS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent] | CallToolResult:
    """Dispatch an MCP tool call to its registered handler.

    :param name: (str) The name of the tool to invoke.
    :param arguments: (dict) The arguments supplied by the MCP client for this tool call.
    :return: (list) The handler's ``types.TextContent`` results, or a single
        error message if ``name`` does not match a registered tool.
    """
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
    """Start the MCP server, selecting transport via the ``MCP_TRANSPORT`` env var."""
    logger.info("project-context-server starting")
    try:
        asyncio.run(_main())
    except Exception:
        logger.exception("Server crashed at top level")
        raise
