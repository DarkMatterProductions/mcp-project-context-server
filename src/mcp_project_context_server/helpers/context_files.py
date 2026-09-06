"""Shared helpers for loading, hashing, and listing individual .context/ files."""
import hashlib
import logging
from pathlib import Path

from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider

logger = logging.getLogger(__name__)


def hash_content(content: str) -> str:
    """Compute the SHA-512 hex digest of *content*.

    :param content: (str) The file content to hash.
    :return: (str) The hex-encoded SHA-512 digest of *content*.
    """
    return hashlib.sha512(content.encode("utf-8")).hexdigest()


def format_tagged_file(path: str, sha512: str, content: str) -> str:
    """Format *content* as an XML-tagged context-file block.

    :param path: (str) The ``.context/``-relative path of the file.
    :param sha512: (str) The SHA-512 hex digest of *content*.
    :param content: (str) The file's contents.
    :return: (str) A ``<context-file path="..." sha512="...">`` tagged block.
    """
    return f'<context-file path="{path}" sha512="{sha512}">\n{content}\n</context-file>'


def _is_safe_relative_path(rel_path: str) -> bool:
    """Reject absolute paths and paths containing ``..`` segments.

    These tools are reachable over the ``sse`` transport where input is not
    necessarily trusted, so a requested path must stay within ``.context/``.
    """
    p = Path(rel_path)
    if p.is_absolute():
        return False
    return ".." not in p.parts


async def resolve_requested_files(project_path: str, rel_paths: list[str]) -> tuple[dict[str, str], list[str]]:
    """Resolve a list of ``.context/``-relative paths to their contents.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param rel_paths: (list) POSIX-style paths relative to ``.context/``.
    :return: (tuple) A ``(found, missing)`` pair — ``found`` maps requested paths to
        their contents; ``missing`` lists requested paths that could not be
        resolved (not found on disk/remote, or rejected as unsafe).
    """
    logger.debug(f"Executing 'resolve_requested_files' with the argument rel_paths: {rel_paths}")
    safe_paths = [p for p in rel_paths if _is_safe_relative_path(p)]

    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(project_path, provider.provider_name)
    found: dict[str, str] = {}

    if is_remote:
        try:
            files = await provider.fetch_context_files(resolved_path)
        except RepositoryError:
            files = {}
        found = {p: files[p] for p in safe_paths if p in files}
    else:
        context_dir = find_context_dir(resolved_path)
        if context_dir is not None:
            for p in safe_paths:
                candidate = context_dir / p
                if candidate.is_file():
                    found[p] = candidate.read_text(encoding="utf-8")

    missing = [p for p in rel_paths if p not in found]
    return found, missing


async def list_context_files(project_path: str, prefix: str) -> list[str]:
    """List sorted ``.context/``-relative markdown paths starting with *prefix*.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param prefix: (str) A POSIX-style path prefix, e.g. ``"sessions/"``.
    :return: (list) Sorted relative paths (POSIX-style) starting with *prefix*.
    """
    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(project_path, provider.provider_name)

    if is_remote:
        try:
            files = await provider.fetch_context_files(resolved_path)
        except RepositoryError:
            return []
        return sorted(k for k in files if k.startswith(prefix))

    context_dir = find_context_dir(resolved_path)
    if context_dir is None:
        return []

    all_paths = (m.relative_to(context_dir).as_posix() for m in context_dir.rglob("*.md"))
    return sorted(p for p in all_paths if p.startswith(prefix))
