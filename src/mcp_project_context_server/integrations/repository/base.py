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
        """Fetch all .md files from the .context/ directory of the repository."""
        ...

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of .context/BUNDLE.md, or None if it does not exist."""
        ...

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository."""
        ...

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Write (create or update) a file in the repository.

        Args:
            branch: Target branch. Falls back to the provider's default
                branch when ``None``. Ignored by the local provider.
        """
        ...

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        A no-op for the local provider, which has no notion of a remote ref.
        """
        ...

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch name for the repository."""
        ...

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible via this provider."""
        ...


class RepositoryError(Exception):
    """Raised when a repository provider operation fails."""


def normalize_repo_identifier(raw: str) -> str:
    """Normalise a repo identifier to ``owner/repo`` form.

    Accepts a full ``http(s)://`` URL (the last two path segments are
    extracted and joined) or an already-short ``owner/repo`` identifier
    (returned unchanged).
    """
    if raw.startswith("http://") or raw.startswith("https://"):
        parts = urlparse(raw).path.strip("/").split("/")
        return "/".join(parts[-2:])
    return raw
