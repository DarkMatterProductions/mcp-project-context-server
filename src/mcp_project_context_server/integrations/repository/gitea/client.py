"""Gitea repository provider implementation using the Gitea REST API."""

import base64
import os
from typing import Optional
from urllib.parse import urlparse

import httpx

from mcp_project_context_server.integrations.repository.base import RepositoryError, RepositoryInfo

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GiteaRepositoryProvider:
    """Repository provider that communicates with a self-hosted Gitea instance.

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — Gitea access token.
    * ``REPO_BASE_URL`` — **Required** Gitea instance URL (no default).
      The API base is derived as ``{REPO_BASE_URL}/api/v1``.
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name (default: ``"main"``).

    Raises:
        EnvironmentError: If ``REPO_BASE_URL`` is not set.
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables."""
        self._token: str = os.getenv("REPO_AUTH_TOKEN", "")
        base = os.getenv("REPO_BASE_URL", "").rstrip("/")
        if not base:
            raise EnvironmentError(
                "REPO_BASE_URL is required for the Gitea provider. "
                "Set it to your Gitea instance URL (e.g. https://gitea.example.com)."
            )
        self._api_base: str = f"{base}/api/v1"
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "gitea"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to ``owner/repo`` form."""
        if repo_id.startswith("http://") or repo_id.startswith("https://"):
            parts = urlparse(repo_id).path.strip("/").split("/")
            return "/".join(parts[-2:])
        return repo_id

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for Gitea API requests."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"token {self._token}"
        return headers

    def _split(self, repo_id: str) -> tuple[str, str]:
        """Return *(owner, repo)* from a normalised ``owner/repo`` string."""
        owner, repo = self._normalise_repo_id(repo_id).split("/", 1)
        return owner, repo

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` subtree of the repository.

        Returns an empty dict on 404.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            for item in tree:
                path: str = item.get("path", "")
                if path.startswith(".context/") and path.endswith(".md"):
                    rel = path.removeprefix(".context/")
                    raw = await client.get(
                        f"{self._api_base}/repos/{owner}/{repo}/raw/.context/{rel}" f"?ref={branch}",
                        headers=self._headers(),
                    )
                    if raw.status_code == 200:
                        result[rel] = raw.text
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``."""
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/raw/.context/BUNDLE.md?ref={branch}",
                headers=self._headers(),
            )
            if resp.status_code == 200:
                return resp.text
            return None

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository tree.

        Capped at 200 files.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            candidates = [item for item in tree if _has_source_extension(item.get("path", ""))][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                raw = await client.get(
                    f"{self._api_base}/repos/{owner}/{repo}/raw/{path}?ref={branch}",
                    headers=self._headers(),
                )
                if raw.status_code == 200:
                    result[path] = raw.text
        return result

    async def write_file(self, repo_id: str, path: str, content: str, message: str) -> None:
        """Create or update *path* in the repository.

        Raises :exc:`RepositoryError` if the API returns a non-success status.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        async with httpx.AsyncClient() as client:
            # Check if file exists to get SHA
            check = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
            )
            if check.status_code == 200:
                sha = check.json().get("sha", "")
                payload = {"message": message, "content": encoded, "sha": sha, "branch": branch}
                resp = await client.patch(
                    f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                    json=payload,
                )
            else:
                payload = {"message": message, "content": encoded, "branch": branch}
                resp = await client.post(
                    f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                    json=payload,
                )
            if not resp.is_success:
                raise RepositoryError(f"Gitea write_file failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``."""
        owner, repo = self._split(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._api_base}/repos/{owner}/{repo}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json().get("default_branch", self._default_branch_fallback)
        except Exception:
            pass
        return self._default_branch_fallback

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible to the configured token.

        If *org* is set, lists repositories for that organisation.  Otherwise
        searches all accessible repositories.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._api_base}/orgs/{org}/repos"
            else:
                params = "limit=50"
                if self._token:
                    params += f"&token={self._token}"
                url = f"{self._api_base}/repos/search?{params}"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            # /repos/search returns {"data": [...]} while /orgs/{org}/repos returns [...]
            items = data.get("data", data) if isinstance(data, dict) else data
            return [_repo_info_from_gitea(r) for r in items]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


def _repo_info_from_gitea(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a Gitea API repository object."""
    return RepositoryInfo(
        identifier=data.get("full_name", ""),
        name=data.get("name", ""),
        description=data.get("description") or "",
        indexed=False,
    )
