"""Tool: list_repositories — list accessible repositories via the configured provider."""
import logging

from mcp import types
from mcp.types import CallToolResult, TextContent

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import (
    get_repository_provider,
    validate_repo_access,
)

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> CallToolResult:
    """Handle the ``list_repositories`` tool call.

    :param arguments: (dict) Tool input dict. Optional key ``"org"`` filters by
        organisation/group name.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item.
    """
    org = arguments.get("org")
    try:
        provider = get_repository_provider()
        repos = await provider.list_repositories(org=org)
    except Exception as exc:
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Error listing repositories: {exc}")])

    # Only surface repositories the allowlist actually permits — in
    # multi-tenant mode the provider may still be able to see repos outside
    # APPROVED_ORGS/APPROVED_REPOS (e.g. via a broadly-scoped API token).
    allowed_repos = []
    for r in repos:
        try:
            validate_repo_access(r.identifier)
        except RepositoryError:
            continue
        allowed_repos.append(r)
    repos = allowed_repos

    if not repos:
        return types.CallToolResult(content=[types.TextContent(type="text", text="No repositories found.")])
    repos_structured_results = {}
    repos_content_results = []
    for r in repos:
        status = "indexed" if r.indexed else "not indexed"
        last_indexed = f" (last indexed: {r.last_indexed})" if r.last_indexed else ""
        repos_content_results.append(types.TextContent(type="text", text=f"- **{r.identifier}** — {r.description or 'no description'} [{status}{last_indexed}]"))
        repos_structured_results[r.identifier] = {
            "identifier": types.TextContent(type="text", text=r.identifier),
            "description": types.TextContent(type="text", text=r.description or 'no description'),
            "status": types.TextContent(type="text", text=status),
            "last_indexed": types.TextContent(type="text", text=last_indexed),
        }
    return types.CallToolResult(content=repos_content_results, structuredContent=repos_structured_results)
