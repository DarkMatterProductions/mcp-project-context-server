"""Local filesystem repository provider implementation."""

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from mcp_project_context_server.integrations.repository.base import RepositoryInfo

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_SKIP_DIRS: frozenset[str] = frozenset({".git", "node_modules", ".venv", "__pycache__", "dist", "build"})
_MAX_SOURCE_FILES = 500


class LocalRepositoryProvider:
    """Repository provider that reads from the local filesystem.

    ``repo_id`` for all methods is always a filesystem path (str or Path).
    """

    def __init__(self) -> None:
        """Initialize the provider, reading PROJECT_PATH from the environment."""
        self._project_path: str = os.getenv("PROJECT_PATH", "")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "local"

    @staticmethod
    async def fetch_context_files(repo_id: str) -> dict[str, str]:
        """Read all .md files from ``<repo_id>/.context/`` recursively.

        Returns a dict keyed by POSIX relative paths.  Returns an empty dict if
        the ``.context/`` directory does not exist.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (dict) A mapping of POSIX-style relative markdown file paths to their contents.
        """
        logger.debug(f"Executing 'fetch_context_files' with the arguments repo_id: {repo_id}")
        context_dir = Path(repo_id) / ".context"
        if not context_dir.is_dir():
            return {}
        result: dict[str, str] = {}
        for md_file in context_dir.rglob("*.md"):
            key = md_file.relative_to(context_dir).as_posix()
            result[key] = md_file.read_text(encoding="utf-8")
        return result

    @staticmethod
    async def fetch_source_bundle(repo_id: str) -> Optional[str]:
        """Return the content of ``<repo_id>/.context/BUNDLE.md``, or None.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        logger.debug(f"Executing 'fetch_source_bundle' with the arguments repo_id: {repo_id}")
        bundle = Path(repo_id) / ".context" / "BUNDLE.md"
        if bundle.is_file():
            return bundle.read_text(encoding="utf-8")
        return None

    @staticmethod
    async def fetch_source_files(repo_id: str) -> dict[str, str]:
        """Return source code files under ``repo_id``, skipping common non-source dirs.

        Capped at ``_MAX_SOURCE_FILES`` (500) entries.  Keys are POSIX paths
        relative to ``repo_id``.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (dict) A mapping of POSIX-style relative source file paths to their contents.
        """
        logger.debug(f"Executing 'fetch_source_files' with the arguments repo_id: {repo_id}")
        root = Path(repo_id)
        result: dict[str, str] = {}
        for file_path in _walk_source_files(root):
            if len(result) >= _MAX_SOURCE_FILES:
                break
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            key = file_path.relative_to(root).as_posix()
            result[key] = content
        return result

    @staticmethod
    async def write_file(
        repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Write ``content`` to ``<repo_id>/<path>``, creating parent directories.

        ``message`` and ``branch`` are ignored for the local provider (no
        commit is made; writes always land on whatever is checked out).

        :param repo_id: (str) Filesystem path to the project root.
        :param path: (str) The file path to write, relative to ``repo_id``.
        :param content: (str) The new full contents of the file.
        :param message: (str) Ignored by the local provider.
        :param branch: (str) Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        logger.debug(f"Executing 'write_file' with the arguments repo_id: {repo_id}, path: {path}, content: {content}, message: {message}, branch: {branch}")
        target = Path(repo_id) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    @staticmethod
    async def create_branch(repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """No-op: the local provider writes directly to disk regardless of branch.

        :param repo_id: (str) Filesystem path to the project root.
        :param new_branch: (str) Ignored by the local provider.
        :param from_branch: (str) Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        logger.debug(f"Executing 'create_branch' with the arguments repo_id: {repo_id}, new_branch: {new_branch}, from_branch: {from_branch}")
        return None

    @staticmethod
    async def get_default_branch(repo_id: str) -> str:
        """Return the current git branch for the repository, falling back to ``"main"``.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (str) The current git branch name, or ``"main"`` if it cannot be determined.
        """
        logger.debug(f"Executing 'get_default_branch' with the arguments repo_id: {repo_id}")

        def _run_git() -> str:
            result = subprocess.run(
                ["git", "-C", str(repo_id), "symbolic-ref", "--short", "HEAD"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "main"

        return await asyncio.to_thread(_run_git)

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """Return a single-element list for the project path from ``PROJECT_PATH``.

        Returns an empty list if ``PROJECT_PATH`` is not set.  ``org`` is ignored
        for the local provider.

        :param org: (str) Ignored by the local provider.
        :return: (list) A single-element list describing the ``PROJECT_PATH`` project,
            or an empty list if ``PROJECT_PATH`` is not set.
        """
        logger.debug(f"Executing 'list_repositories' with the arguments org: {org}")
        if not self._project_path:
            return []
        p = Path(self._project_path)
        return [
            RepositoryInfo(
                identifier=self._project_path,
                name=p.name,
                description="",
                indexed=False,
            )
        ]


def _walk_source_files(root: Path):
    """Yield source files under *root*, skipping known non-source directories."""
    logger.debug(f"Executing '_walk_source_files' with the arguments org: {root}")
    for entry in root.iterdir():
        if entry.is_dir():
            if entry.name in _SKIP_DIRS:
                continue
            yield from _walk_source_files(entry)
        elif entry.is_file() and entry.suffix in _SOURCE_EXTENSIONS:
            yield entry
