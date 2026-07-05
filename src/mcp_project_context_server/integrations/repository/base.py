"""RepositoryProvider Protocol and shared data types."""

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable
from urllib.parse import urlparse


@dataclass
class RepositoryInfo:
    """Metadata about a single repository."""

    identifier: str  # e.g. "DarkMatterProductions/vs-cartographytable"
    name: str
    description: str
    indexed: bool  # True if a vector collection exists for this repo
    last_indexed: Optional[str] = None  # ISO datetime string or None


@runtime_checkable
class RepositoryProvider(Protocol):
    """Protocol that all repository provider implementations must satisfy."""

    @property
    def provider_name(self) -> str:
        """Short identifier, e.g. ``"local"``, ``"github"``, ``"gitlab"``, ``"gitea"``."""
        ...

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the .context/ directory of the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        ...

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of .context/BUNDLE.md, or None if it does not exist.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (str) The contents of ``.context/BUNDLE.md``, or ``None`` if it does not exist.
        """
        ...

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        ...

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Write (create or update) a file in the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :param path: (str) The path of the file to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the provider's default
            branch when ``None``. Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        ...

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        A no-op for the local provider, which has no notion of a remote ref.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        """
        ...

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch name for the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (str) The name of the repository's default branch.
        """
        ...

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible via this provider.

        :param org: (str) Optional organisation/group name to filter results by.
        :return: (list) The accessible ``RepositoryInfo`` entries, optionally filtered by ``org``.
        """
        ...


class RepositoryError(Exception):
    """Raised when a repository provider operation fails."""


def normalize_repo_identifier(raw: str) -> str:
    """Normalise a repo identifier to ``owner/repo`` form.

    Accepts a full ``http(s)://`` URL (the last two path segments are
    extracted and joined) or an already-short ``owner/repo`` identifier
    (returned unchanged).

    :param raw: (str) A full repository URL or a short ``owner/repo`` identifier.
    :return: (str) The normalised ``owner/repo`` identifier.
    """
    if raw.startswith("http://") or raw.startswith("https://"):
        parts = urlparse(raw).path.strip("/").split("/")
        return "/".join(parts[-2:])
    return raw
