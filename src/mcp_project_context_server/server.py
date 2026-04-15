"""MCP server setup, tool registry, and entry point."""

import asyncio
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from mcp_project_context_server.tools import (
    load_context,
    search_context,
    save_session,
    index_context,
)


_LOG_PATH = Path(r"C:\Users\drahk\.mcp-data\logs\project-context-server.log")
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
                    "description": "Absolute path to the project root or any file within it.",
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
]

_TOOL_HANDLERS = {
    "load_project_context":  load_context.handle,
    "search_project_context": search_context.handle,
    "save_session_summary":  save_session.handle,
    "index_project_context": index_context.handle,
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
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run() -> None:
    logger.info("project-context-server starting")
    try:
        asyncio.run(_main())
    except Exception:
        logger.exception("Server crashed at top level")
        raise