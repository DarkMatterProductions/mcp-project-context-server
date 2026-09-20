"""Tool: create_adr — allocate the next ADR number and write a new ADR stub."""
import logging
import os
import re

from mcp import types

from mcp_project_context_server.helpers.adr import list_adrs
from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.helpers.repo_write import append_reindex_note, write_context_file
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access

logger = logging.getLogger(__name__)

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

_TEMPLATE = """# ADR-{number:05d}: {title}

## Status
Proposed

## Context
{context}

## ADR Review Discussion
[Discussion pending]

## Decision
[Pending review]

## Consequences
[Pending review]

## Alternatives Considered
[Pending review]
"""


def _kebab_case(title: str) -> str:
    """Convert *title* to a kebab-case slug for use in an ADR filename."""
    slug = _NON_ALNUM_RE.sub("-", title.strip().lower()).strip("-")
    return slug or "untitled"


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``create_adr`` tool call.

    Allocates the next sequential ADR number (``max(existing) + 1``, with no
    lock/retry against concurrent creation — see ADR-00012) and writes a new
    ``Proposed``-status ADR populated with the given title and context, with
    placeholder text in the remaining sections.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``,
        ``"title"``, and ``"context"``. Optional ``"auto_reindex"`` (bool,
        default False).
    :return: (list) A single :class:`~mcp.types.TextContent` item confirming the
        write (and either the re-index result or a manual-reindex reminder), or
        an error message.
    """
    title = arguments["title"].strip()
    context_text = arguments["context"].strip()
    auto_reindex = arguments.get("auto_reindex", False)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    existing, _warnings = await list_adrs(_project_path)
    next_number = max((info.number for info in existing), default=0) + 1
    slug = _kebab_case(title)
    filename = f"ADR-{next_number:05d}-{slug}.md"
    rel_path = f"decisions/{filename}"
    content = _TEMPLATE.format(number=next_number, title=title, context=context_text)

    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(_project_path, provider.provider_name)
    commit_message = f"Create ADR-{next_number:05d}: {title}"

    if is_remote:
        message = await write_context_file(provider, resolved_path, rel_path, content, commit_message)
    else:
        context_dir = find_context_dir(resolved_path)
        if context_dir is None:
            return [
                types.TextContent(
                    type="text",
                    text=f"No .context/ directory found near {arguments['project_path']}",
                )
            ]
        decisions_dir = context_dir / "decisions"
        decisions_dir.mkdir(exist_ok=True)
        (decisions_dir / filename).write_text(content, encoding="utf-8")
        message = f"Created {rel_path}."

    final_text = await append_reindex_note(_project_path, message, auto_reindex)
    return [types.TextContent(type="text", text=final_text)]
