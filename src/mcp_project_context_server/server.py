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
from collections.abc import Callable, Coroutine
from typing import Any, cast

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
    bootstrap_context,
    create_adr,
    edit_adr,
    edit_project,
    find_latest_session_file,
    get_bootstrap_questions,
    index_context,
    list_adr_sections,
    list_adrs,
    list_repositories,
    load_context_files,
    read_adr,
    read_adr_section,
    read_adr_status,
    reload_active_context_file,
    save_session,
    search_adr_index,
    search_adr_sections,
    search_context_index,
    search_session_files,
    update_adr_status,
    write_project,
)

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

logger = logging.getLogger(__name__)


_PROJECT_PATH_PROPERTY = {
    "type": "string",
    "description": ("Absolute filesystem path, a short 'owner/repo' identifier, " "or a full https:// repository URL."),
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

_SEARCH_SECTIONS_OUTPUT_SCHEMA = {
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
                    "section": {
                        "type": ["string", "null"],
                        "description": "Top-level (##) section name the chunk belongs to, if known.",
                    },
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

_NUMBER_OR_FILENAME_PROPERTY = {
    "type": ["string", "integer"],
    "description": (
        "The ADR's number (e.g. 12), short form (e.g. 'ADR-00012', case-insensitive), "
        "or exact filename/path (e.g. 'ADR-00012-topic.md')."
    ),
}

_AUTO_REINDEX_PROPERTY = {
    "type": "boolean",
    "default": False,
    "description": (
        "When true, automatically re-run `index_project_context` after the write and "
        "include its result. When false (default), the response includes a manual-reindex reminder."
    ),
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
    Tool(
        name="list_adrs",
        description=(
            "List every ADR in .context/decisions/ as a lightweight table (number, title, "
            "status, filename). Use this before `read_adr`/`read_adr_section` to find which "
            "ADR you need, without loading full ADR content."
        ),
        input_schema={
            "type": "object",
            "properties": {"project_path": _PROJECT_PATH_PROPERTY},
            "required": ["project_path"],
        },
    ),
    Tool(
        name="read_adr",
        description=(
            "Read one ADR's full raw content by number or filename, tagged with its path and "
            "SHA-512 hash so `reload_active_context_file` can later detect changes. Prefer "
            "`read_adr_section` when you only need one section."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "number_or_filename": _NUMBER_OR_FILENAME_PROPERTY,
            },
            "required": ["project_path", "number_or_filename"],
        },
    ),
    Tool(
        name="read_adr_status",
        description=(
            "Read one ADR's title and parsed Status without loading its full content. "
            "Returns an explicit message for ADRs using the legacy `**Status:**` inline format."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "number_or_filename": _NUMBER_OR_FILENAME_PROPERTY,
            },
            "required": ["project_path", "number_or_filename"],
        },
    ),
    Tool(
        name="list_adr_sections",
        description="List one ADR's top-level (##) section names, in document order.",
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "number_or_filename": _NUMBER_OR_FILENAME_PROPERTY,
            },
            "required": ["project_path", "number_or_filename"],
        },
    ),
    Tool(
        name="read_adr_section",
        description=(
            "Read a single named top-level (##) section of one ADR (e.g. 'Context', "
            "'Decision', 'Consequences'). Use `list_adr_sections` first if you don't know "
            "the exact section name."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "number_or_filename": _NUMBER_OR_FILENAME_PROPERTY,
                "section": {"type": "string", "description": "Exact ## heading text, without the ## marker."},
            },
            "required": ["project_path", "number_or_filename", "section"],
        },
    ),
    Tool(
        name="search_adr_sections",
        description=(
            "Semantically search within a single resolved ADR, scoped by number or filename. "
            "Use this to find relevant sections/passages inside one ADR you've already identified "
            "(e.g. via `list_adrs` or `search_adr_index`)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "number_or_filename": _NUMBER_OR_FILENAME_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "number_or_filename", "query"],
        },
        output_schema=_SEARCH_SECTIONS_OUTPUT_SCHEMA,
    ),
    Tool(
        name="create_adr",
        description=(
            "Create a new ADR: allocates the next sequential number, writes a "
            "'Proposed'-status stub with the given title and context, and placeholder text "
            "in the remaining sections (Decision, Consequences, Alternatives Considered, "
            "ADR Review Discussion). No lock/retry against concurrent creation."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "title": {"type": "string", "description": "The ADR's topic title (used verbatim in the heading)."},
                "context": {"type": "string", "description": "The Context section's content."},
                "auto_reindex": _AUTO_REINDEX_PROPERTY,
            },
            "required": ["project_path", "title", "context"],
        },
    ),
    Tool(
        name="edit_adr",
        description=(
            "Replace a single named top-level (##) section of one ADR. Rejects the 'Status' "
            "section — use `update_adr_status` for status transitions instead."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "number_or_filename": _NUMBER_OR_FILENAME_PROPERTY,
                "section": {"type": "string", "description": "Exact ## heading text, without the ## marker."},
                "content": {"type": "string", "description": "The section's new body, excluding the heading line."},
                "auto_reindex": _AUTO_REINDEX_PROPERTY,
            },
            "required": ["project_path", "number_or_filename", "section", "content"],
        },
    ),
    Tool(
        name="update_adr_status",
        description=(
            "Transition one ADR's Status, with lifecycle guardrails: rejects unknown statuses; "
            "requires the target ADR to already exist for 'Superseded by ADR-XXXXX'; requires an "
            "'explanation' for unusual (non-adjacent-forward) transitions; requires a populated "
            "Decision section (or an 'explanation' to fold into it) before moving to 'Accepted'; "
            "and removes the 'ADR Review Discussion' section once 'Accepted' is reached."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "number_or_filename": _NUMBER_OR_FILENAME_PROPERTY,
                "new_status": {
                    "type": "string",
                    "description": (
                        "One of: Proposed, Under Review, Accepted, Implemented, Deprecated, "
                        "or 'Superseded by ADR-XXXXX'."
                    ),
                },
                "explanation": {
                    "type": "string",
                    "description": (
                        "Required for unusual transitions and for reaching 'Accepted' with an "
                        "unpopulated Decision section. Also appended as a timestamped entry to "
                        "'ADR Review Discussion' when the ADR is currently Proposed/Under Review."
                    ),
                },
                "auto_reindex": _AUTO_REINDEX_PROPERTY,
            },
            "required": ["project_path", "number_or_filename", "new_status"],
        },
    ),
    Tool(
        name="write_project",
        description="Overwrite the full content of .context/project.md.",
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "content": {"type": "string", "description": "The full new content of project.md."},
                "auto_reindex": _AUTO_REINDEX_PROPERTY,
            },
            "required": ["project_path", "content"],
        },
    ),
    Tool(
        name="edit_project",
        description="Replace a single named top-level (##) section of .context/project.md.",
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "section": {"type": "string", "description": "Exact ## heading text, without the ## marker."},
                "content": {"type": "string", "description": "The section's new body, excluding the heading line."},
                "auto_reindex": _AUTO_REINDEX_PROPERTY,
            },
            "required": ["project_path", "section", "content"],
        },
    ),
    Tool(
        name="get_bootstrap_questions",
        description=(
            "Get the interview question set for a bootstrap artifact (currently 'project', "
            "for .context/project.md). Ask the user each question, then pass the answers as "
            "`project_sections` to `bootstrap_context`. Pass `project_path` to also merge in "
            "any repo-supplied custom questions from a `.project-bootstrap-questions.yaml` file "
            "at the repository root."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "default": "project",
                    "description": "The bootstrap artifact to get interview questions for.",
                },
                "project_path": _PROJECT_PATH_PROPERTY,
            },
            "required": [],
        },
    ),
    Tool(
        name="bootstrap_context",
        description=(
            "Atomically scaffold a brand-new .context/ directory for a project that doesn't "
            "have one yet: creates decisions/ and sessions/, writes the bundled "
            "ADR_CREATE_AND_MANAGEMENT.md and PLANNING_LOOP.md governance docs, writes an "
            "interview-driven project.md (answers from `get_bootstrap_questions`), and creates "
            "a governance ADR-00001 establishing the project's ADR process. Every step is "
            "additive and idempotent — artifacts that already exist are skipped, not overwritten. "
            "If the repository has a `.project-bootstrap-questions.yaml` file at its root, its "
            "questions are merged into the interview set used for project.md."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "project_name": {"type": "string", "description": "The project's name, used in project.md's title."},
                "project_sections": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": (
                        "Interview answers keyed by the 'key' fields from "
                        "`get_bootstrap_questions('project')`, e.g. {'One-liner': '...'}."
                    ),
                },
                "auto_reindex": _AUTO_REINDEX_PROPERTY,
            },
            "required": ["project_path", "project_name"],
        },
    ),
]

ToolHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, list[TextContent] | CallToolResult]]

_TOOL_HANDLERS: dict[str, ToolHandler] = {
    "search_context_index": search_context_index.handle,
    "search_adr_index": search_adr_index.handle,
    "search_session_files": search_session_files.handle,
    "find_latest_session_file": find_latest_session_file.handle,
    "load_context_files": load_context_files.handle,
    "reload_active_context_file": reload_active_context_file.handle,
    "save_session_summary": save_session.handle,
    "index_project_context": index_context.handle,
    "list_repositories": list_repositories.handle,
    "list_adrs": list_adrs.handle,
    "read_adr": read_adr.handle,
    "read_adr_status": read_adr_status.handle,
    "list_adr_sections": list_adr_sections.handle,
    "read_adr_section": read_adr_section.handle,
    "search_adr_sections": search_adr_sections.handle,
    "create_adr": create_adr.handle,
    "edit_adr": edit_adr.handle,
    "update_adr_status": update_adr_status.handle,
    "write_project": write_project.handle,
    "edit_project": edit_project.handle,
    "get_bootstrap_questions": get_bootstrap_questions.handle,
    "bootstrap_context": bootstrap_context.handle,
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
        result = await handler(params.arguments or {})
    except Exception as exc:
        logger.exception("Tool '%s' raised an unhandled exception", params.name)
        return CallToolResult(content=[TextContent(type="text", text=str(exc))], is_error=True)
    if isinstance(result, CallToolResult):
        return result
    return CallToolResult(content=cast(list[Any], result))


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
