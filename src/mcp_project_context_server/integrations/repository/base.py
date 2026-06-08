"""RepositoryProvider Protocol and shared data types."""

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable


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

    async def write_file(self, repo_id: str, path: str, content: str, message: str) -> None:
        """Write (create or update) a file in the repository."""
        ...

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch name for the repository."""
        ...

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible via this provider."""
        ...


class RepositoryError(Exception):
    """Raised when a repository provider operation fails."""
