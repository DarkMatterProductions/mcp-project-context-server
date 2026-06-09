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
    find_latest_session_file,
    index_context,
    list_repositories,
    load_context_files,
    reload_active_context_file,
    save_session,
    search_adr_index,
    search_context_index,
    search_session_files,
)

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

logger = logging.getLogger(__name__)


_PROJECT_PATH_PROPERTY = {
    "type": "string",
    "description": (
        "Absolute filesystem path, a short 'owner/repo' identifier, " "or a full https:// repository URL."
    ),
}

_SEARCH_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "description": "Individual matching hits, one per matched chunk.",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": ".context/-relative path of the matched file."},
                    "chunk": {"type": ["integer", "null"], "description": "Chunk index within the file, if known."},
                    "content": {"type": "string", "description": "The matching chunk's text."},
                    "distance": {"type": ["number", "null"], "description": "Vector distance to the query, if known."},
                },
                "required": ["file", "content"],
            },
        },
        "warning": {
            "type": "string",
            "description": "Present only when the index was built with a different embedding provider/model.",
        },
    },
    "required": ["results"],
}

_TOOL_DEFINITIONS: list[Tool] = [
    Tool(
        name="search_context_index",
        description=(
            "Semantically search the whole indexed project context. "
            "Use this first to find which files are relevant to your task, then "
            "pass their paths to `load_context_files` — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="search_adr_index",
        description=(
            "Semantically search only the architecture decision records under "
            ".context/decisions/. Use this to find ADRs relevant to your current "
            "task, then pass their paths to `load_context_files` — do not rely on this tool's "
            "snippets alone. If you need to search across all files in the project, use "
            "`search_project_files` instead."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="search_session_files",
        description=(
            "Semantically search only past session summaries under .context/sessions/. "
            "Use this to find prior session notes relevant to a topic, then pass their "
            "paths to `load_context_files` — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="find_latest_session_file",
        description=(
            "Deterministically find the most recent .context/sessions/*.md file "
            "(sorted by filename, not semantic relevance). Pass the returned path "
            "to `load_context_files` to load it — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {"project_path": _PROJECT_PATH_PROPERTY},
            "required": ["project_path"],
        },
    ),
    Tool(
        name="load_context_files",
        description=(
            "Load specific .context/-relative files into the active context. "
            "Each loaded file is tagged with its path and a SHA-512 hash of its "
            "contents so `reload_active_context_file` can later detect changes. "
            "Only pass files you actually need — do not load the whole .context/ tree."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of .context/-relative file paths to load, e.g. 'decisions/0007-use-pgvector.md'.",
                },
            },
            "required": ["project_path", "files"],
        },
    ),
    Tool(
        name="reload_active_context_file",
        description=(
            "Check whether files currently held in active context (previously loaded via "
            "`load_context_files`) have changed on disk, by comparing their known SHA-512 "
            "hash against the current one. Returns fresh tagged content for changed files, "
            "a short 'no change' message for unchanged files, and 'not found' for deleted files."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "known_sha512": {"type": "string"},
                        },
                        "required": ["path", "known_sha512"],
                    },
                    "description": "List of {path, known_sha512} entries for files currently in active context.",
                },
            },
            "required": ["project_path", "files"],
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
    "search_context_index": search_context_index.handle,
    "search_adr_index": search_adr_index.handle,
    "search_session_files": search_session_files.handle,
    "find_latest_session_file": find_latest_session_file.handle,
    "load_context_files": load_context_files.handle,
    "reload_active_context_file": reload_active_context_file.handle,
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