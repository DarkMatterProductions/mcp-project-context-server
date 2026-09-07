"""Tool: edit_adr — replace a single named top-level section of an ADR."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.adr import replace_section, resolve_adr
from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.helpers.repo_write import append_reindex_note, write_context_file
from mcp_project_context_server.helpers.sections import split_sections
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``edit_adr`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``,
        ``"number_or_filename"``, ``"section"`` (the exact ``##`` heading text,
        without the ``##`` marker), and ``"content"`` (the section's new body,
        excluding the heading line). Optional ``"auto_reindex"`` (bool, default
        False).
    :return: (list) A single :class:`~mcp.types.TextContent` item confirming the
        write (and either the re-index result or a manual-reindex reminder), or
        an error message.
    """
    number_or_filename = arguments["number_or_filename"]
    section_name = arguments["section"]
    new_content = arguments["content"]
    auto_reindex = arguments.get("auto_reindex", False)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    if section_name.strip().lower() == "status":
        return [
            types.TextContent(
                type="text",
                text="Use `update_adr_status` to change an ADR's Status section, not `edit_adr`.",
            )
        ]

    resolution = await resolve_adr(_project_path, number_or_filename)
    if resolution.error:
        return [types.TextContent(type="text", text=resolution.error)]

    info = resolution.info
    content = resolution.content
    assert info is not None
    assert content is not None

    updated = replace_section(content, section_name, new_content)
    if updated is None:
        available = [s.name for s in split_sections(content) if s.name]
        available_text = ", ".join(available) if available else "none"
        return [
            types.TextContent(
                type="text",
                text=(
                    f"No section named '{section_name}' found in ADR-{info.number:05d} "
                    f"({info.filename}). Available sections: {available_text}."
                ),
            )
        ]

    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(_project_path, provider.provider_name)
    commit_message = f"Update '{section_name}' section of {info.filename}"

    if is_remote:
        message = await write_context_file(provider, resolved_path, info.path, updated, commit_message)
    else:
        context_dir = find_context_dir(resolved_path)
        if context_dir is None:
            return [
                types.TextContent(
                    type="text",
                    text=f"No .context/ directory found near {arguments['project_path']}",
                )
            ]
        (context_dir / info.path).write_text(updated, encoding="utf-8")
        message = f"Updated section '{section_name}' in {info.path}."

    final_text = await append_reindex_note(_project_path, message, auto_reindex)
    return [types.TextContent(type="text", text=final_text)]
