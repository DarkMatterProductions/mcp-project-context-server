"""Shared remote write-mode plumbing for the ADR and project.md write tools.

Local-provider writes stay inline in each tool (``find_context_dir`` + direct
filesystem writes) since local preconditions (e.g. creating ``decisions/``)
differ per tool. This module only covers the remote path, generalized from
``tools/save_session.py``'s ``_handle_remote``.
"""

import logging
import os
from datetime import datetime

from mcp_project_context_server.integrations.repository.base import RepositoryError, RepositoryProvider

logger = logging.getLogger(__name__)


async def write_context_file(
    provider: RepositoryProvider, repo_id: str, rel_path: str, content: str, commit_message: str
) -> str:
    """Write *content* to a ``.context/``-relative path on a remote repository.

    Write target is configurable via ``REPO_ADR_WRITE_MODE``:

    * ``"branch"`` *(default)* — create a new branch (``mcp-adr/{date}-{HHMMSS}``)
      off the default branch and write there, leaving the target branch untouched
      for review. This is the opposite default of ``REPO_SESSION_WRITE_MODE``,
      since ADR/project.md edits are higher-stakes than session-summary appends.
    * ``"direct"`` — write straight to ``REPO_ADR_BRANCH`` if set, otherwise the
      repository's default branch.

    :param provider: (RepositoryProvider) The active repository provider.
    :param repo_id: (str) The resolved repository identifier.
    :param rel_path: (str) The ``.context/``-relative path to write, e.g.
        ``"decisions/ADR-00012-....md"`` or ``"project.md"``.
    :param content: (str) The full new content of the file.
    :param commit_message: (str) The commit message describing the write.
    :return: (str) A human-readable message describing where the content was
        written, or an error message if the write failed.
    """
    target_path = f".context/{rel_path}"
    write_mode = os.getenv("REPO_ADR_WRITE_MODE", "branch").strip().lower()

    try:
        if write_mode == "direct":
            target_branch = os.getenv("REPO_ADR_BRANCH") or None
            await provider.write_file(repo_id, target_path, content, commit_message, branch=target_branch)
            branch_label = target_branch or await provider.get_default_branch(repo_id)
            return (
                f"Wrote `{rel_path}` to `{repo_id}` on branch `{branch_label}` "
                f"(provider: {provider.provider_name})."
            )

        today = datetime.now().strftime("%Y-%m-%d")
        branch_name = f"mcp-adr/{today}-{datetime.now().strftime('%H%M%S')}"
        await provider.create_branch(repo_id, branch_name)
        await provider.write_file(repo_id, target_path, content, commit_message, branch=branch_name)
        return (
            f"Wrote `{rel_path}` to new branch `{branch_name}` on `{repo_id}` " f"(provider: {provider.provider_name})."
        )
    except RepositoryError as exc:
        return f"Error writing `{rel_path}`: {exc}"


async def append_reindex_note(project_path: str, message: str, auto_reindex: bool) -> str:
    """Append either a re-index result or a manual-reindex reminder to *message*.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param message: (str) The write result message to append to.
    :param auto_reindex: (bool) When True, run ``index_project_context`` now and
        append its result; when False, append a reminder to run it manually.
    :return: (str) *message* with the appropriate note appended.
    """
    if not auto_reindex:
        return f"{message}\n\nRun `index_project_context` to make this change searchable."

    from mcp_project_context_server.tools import index_context

    result = await index_context.handle({"project_path": project_path})
    return f"{message}\n\n{result[0].text}"
