"""Tool: list_repositories — list accessible repositories via the configured provider."""

from mcp import types

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import (
    get_repository_provider,
    validate_repo_access,
)


async def handle(arguments: dict) -> list[types.TextContent]:
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
        return [types.TextContent(type="text", text=f"Error listing repositories: {exc}")]

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
        return [types.TextContent(type="text", text="No repositories found.")]
    lines = []
    for r in repos:
        status = "indexed" if r.indexed else "not indexed"
        last = f" (last indexed: {r.last_indexed})" if r.last_indexed else ""
        lines.append(f"- **{r.identifier}** — {r.description or 'no description'} [{status}{last}]")
    return [types.TextContent(type="text", text="\n".join(lines))]
