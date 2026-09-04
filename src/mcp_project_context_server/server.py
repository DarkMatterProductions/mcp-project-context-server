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


from mcp.server import Server, ServerRequestContext
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool,
)

from mcp_project_context_server.tools import (
    index_context,
    list_repositories,
    load_context,
    save_session,
    search_context,
)

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

logger = logging.getLogger(__name__)


_TOOL_DEFINITIONS: list[Tool] = [
    Tool(
        name="load_project_context",
        description=(
            "Load the full project context for the given project path. "
            "Returns project.md, all ADRs, and the latest session summary. "
            "You MUST call this at the start of every session."
        ),
        input_schema={
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
    Tool(
        name="search_project_context",
        description=(
            "Semantically search the indexed project context. "
            "Use this to find relevant past decisions, architecture notes, "
            "or code summaries related to your current task."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string"},
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
    ),
    Tool(
        name="save_session_summary",
        description=(
            "Save a summary of the current session to .context/sessions/YYYY-MM-DD.md. "
            "Call this at the end of a session with a concise summary of what was done."
        ),
        input_schema={
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
    Tool(
        name="index_project_context",
        description=(
            "Re-index the .context/ directory into the vector store. "
            "Run this after updating project.md, adding ADRs, or refreshing BUNDLE.md."
        ),
        input_schema={
            "type": "object",
            "properties": {"project_path": {"type": "string"}},
            "required": ["project_path"],
        },
    ),
    Tool(
        name="list_repositories",
        description=(
            "List repositories accessible via the configured repository provider. "
            "In multi-tenant deployments, use this to discover which repositories are "
            "available before calling other tools.  Optionally filter by organisation name."
        ),
        input_schema={
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


async def list_tools(ctx: ServerRequestContext, params: PaginatedRequestParams | None) -> ListToolsResult:
    """List the MCP tools exposed by this context_server.

    :return: (list) The registered ``Tool`` definitions advertised to MCP clients.
    """
    return ListToolsResult(tools=_TOOL_DEFINITIONS)


async def call_tool(ctx: ServerRequestContext, params: CallToolRequestParams) -> CallToolResult:
    """Dispatch an MCP tool call to its registered handler.

    :param name: (str) The name of the tool to invoke.
    :param arguments: (dict) The arguments supplied by the MCP client for this tool call.
    :return: (CallToolResult) The handler's result normalised into a ``CallToolResult``,
        or a single error message if ``name`` does not match a registered tool.
    """
    handler = _TOOL_HANDLERS.get(params.name)
    if not handler:
        return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {params.name}")])
    try:
        result = await handler(params.arguments)
    except Exception as exc:
        logger.exception("Tool '%s' raised an unhandled exception", params.name)
        return CallToolResult(content=[TextContent(type="text", text=str(exc))], is_error=True)
    if isinstance(result, CallToolResult):
        return result
    return CallToolResult(content=result)


async def _main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport == "stdio":
        from mcp_project_context_server.transport.stdio import run_stdio

        await run_stdio(context_server)

    elif transport == "sse":
        from mcp_project_context_server.transport.sse import run_sse

        await run_sse(context_server)

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


context_server = Server(
    name="project-context",
    version=__version__,
    description=(
        "Project Context Server.  Provides access to project context, "
        "including repomix BUNDLED.md, project.md, ADRs, and session summaries."
        "Use as the primary tool for AI-assisted development, and as the source "
        "of truth for decisions on project development."
    ),
    on_list_tools=list_tools,
    on_call_tool=call_tool,
)