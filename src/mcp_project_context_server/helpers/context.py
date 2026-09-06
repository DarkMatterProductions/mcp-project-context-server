"""Shared helpers for .context/ directory resolution and file reading."""
import logging
import re
from pathlib import Path

from mcp_project_context_server.integrations.repository.base import normalize_repo_identifier

logger = logging.getLogger(__name__)


def find_context_dir(project_path: str | Path) -> Path | None:
    """Walk up from project_path to find a .context/ directory.

    :param project_path: (str) The project root or subdirectory/file path to start searching from.
    :return: (Path) The first ``.context/`` directory found while walking up from
        ``project_path``, or ``None`` if none exists in any parent.
    """
    logger.debug(f"Executing 'find_context_dir' with the argument project_path: {project_path}")
    p = Path(project_path).resolve()
    for candidate in [p, *p.parents]:
        ctx = candidate / ".context"
        if ctx.is_dir():
            return ctx
    return None


def collection_name_for(context_dir: Path) -> str:
    """Derive a stable ChromaDB collection name from the project root.

    Always based on context_dir.parent so it is consistent regardless of
    whether the caller passed a project root, a subdirectory, or a file path.

    :param context_dir: (Path) The project's ``.context/`` directory.
    :return: (str) A sanitized, ChromaDB-safe collection name derived from the
        parent project directory's name, truncated to 63 characters.
    """
    project_name = context_dir.parent.name
    return f"ctx_{project_name}".replace("-", "_").replace(" ", "_")[:63]


def collection_name_for_repo_id(repo_id: str) -> str:
    """Derive a stable ChromaDB collection name from a remote repo identifier.

    Mirrors :func:`collection_name_for`'s sanitization, driven by the
    normalised ``owner/repo`` form so the same collection name is produced
    whether the caller passes a short identifier or a full URL.

    :param repo_id: (str) A short ``owner/repo`` identifier or a full remote repository URL.
    :return: (str) A sanitized, ChromaDB-safe collection name derived from the
        normalized repo identifier, truncated to 63 characters.
    """
    normalized = normalize_repo_identifier(repo_id)
    return f"ctx_{normalized}".replace("-", "_").replace(" ", "_").replace("/", "_")[:63]


def read_context_files(context_dir: Path) -> dict[str, str]:
    """Read all markdown files from .context/ into a dict.

    Keys use POSIX-style forward slashes (Path.as_posix()) so that ChromaDB
    document IDs and metadata are identical on Windows and Linux.

    :param context_dir: (Path) The project's ``.context/`` directory to read markdown files from.
    :return: (dict) A mapping of POSIX-style relative file paths to their markdown file contents.
    """
    return {
        md_file.relative_to(context_dir).as_posix(): md_file.read_text(encoding="utf-8")
        for md_file in context_dir.rglob("*.md")
    }


_SHORT_IDENTIFIER_RE = re.compile(r"^[\w.-]+/[\w.-]+$")


def resolve_project_path(raw: str, provider_name: str) -> tuple[str, bool]:
    """Resolve a raw project path string and determine whether it is remote.

    Remote resolution only applies when *provider_name* is not ``"local"``
    (i.e. ``REPO_PROVIDER`` has been explicitly set to a remote provider).
    When the provider is local, *raw* is always treated as a filesystem path,
    regardless of its shape. See ADR-00024.

    Returns a ``(resolved_path, is_remote)`` tuple.

    * If *provider_name* is ``"local"``: ``is_remote=False`` unconditionally.
    * If *raw* starts with ``http://`` or ``https://``: ``is_remote=True``.
    * If *raw* matches the ``owner/repo`` short identifier pattern
      (``^[\\w.-]+/[\\w.-]+$``): ``is_remote=True``.
    * Otherwise: ``is_remote=False`` (filesystem path — existing behaviour).

    :param raw: (str) The raw project path or identifier supplied by the caller.
    :param provider_name: (str) The active repository provider's name, from
        ``get_repository_provider().provider_name`` (i.e. ``REPO_PROVIDER``).
    :return: (tuple) A two-element tuple ``(resolved_path, is_remote)``.
    """
    logger.debug(f"Executing 'resolve_project_path' with raw: {raw}, provider_name: {provider_name}")
    if provider_name == "local":
        return raw, False
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw, True
    if _SHORT_IDENTIFIER_RE.match(raw):
        return raw, True
    return raw, False
