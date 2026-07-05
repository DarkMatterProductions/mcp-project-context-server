"""GitLab repository provider implementation using the GitLab REST API."""

import os
from typing import Optional
from urllib.parse import quote

import httpx

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    normalize_repo_identifier,
)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GitLabRepositoryProvider:
    """Repository provider that communicates with the GitLab REST API (v4).

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — GitLab personal access token.
    * ``REPO_BASE_URL`` — GitLab instance URL (default: ``https://gitlab.com``).
      The API base is derived as ``{REPO_BASE_URL}/api/v4``.
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name (default: ``"main"``).
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables."""
        self._token: str = os.getenv("REPO_AUTH_TOKEN", "")
        base = os.getenv("REPO_BASE_URL", "https://gitlab.com").rstrip("/")
        self._api_base: str = f"{base}/api/v4"
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "gitlab"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to ``namespace/project`` form."""
        return normalize_repo_identifier(repo_id)

    def _url_encode_id(self, repo_id: str) -> str:
        """URL-encode the ``namespace/project`` string for GitLab's ``:id`` parameter."""
        return quote(self._normalise_repo_id(repo_id), safe="")

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for GitLab API requests."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["PRIVATE-TOKEN"] = self._token
        return headers

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` tree of the repository.

        Returns an empty dict on 404.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/tree"
                f"?path=.context&recursive=true&ref={branch}&per_page=100",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            for item in resp.json():
                if item.get("type") == "blob" and item["name"].endswith(".md"):
                    file_path = item["path"]
                    encoded_path = quote(file_path, safe="")
                    raw = await client.get(
                        f"{self._api_base}/projects/{encoded_id}/repository/files" f"/{encoded_path}/raw?ref={branch}",
                        headers=self._headers(),
                    )
                    if raw.status_code == 200:
                        rel = file_path.removeprefix(".context/")
                        result[rel] = raw.text
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/files" f"/.context%2FBUNDLE.md/raw?ref={branch}",
                headers=self._headers(),
            )
            if resp.status_code == 200:
                return resp.text
            return None

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository tree.

        Capped at 200 files.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/tree" f"?recursive=true&ref={branch}&per_page=100",
                headers=self._headers(),
            )
            resp.raise_for_status()
            candidates = [
                item
                for item in resp.json()
                if item.get("type") == "blob" and _has_source_extension(item.get("path", ""))
            ][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                encoded_path = quote(path, safe="")
                raw = await client.get(
                    f"{self._api_base}/projects/{encoded_id}/repository/files" f"/{encoded_path}/raw?ref={branch}",
                    headers=self._headers(),
                )
                if raw.status_code == 200:
                    result[path] = raw.text
        return result

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Create or update *path* in the repository.

        Writes to *branch* if given, otherwise the repository's default
        branch.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :param path: (str) The file path to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        encoded_id = self._url_encode_id(repo_id)
        target_branch = branch or await self.get_default_branch(repo_id)
        encoded_path = quote(path, safe="")
        payload = {"branch": target_branch, "content": content, "commit_message": message}
        async with httpx.AsyncClient() as client:
            # Check if file exists
            head = await client.head(
                f"{self._api_base}/projects/{encoded_id}/repository/files/{encoded_path}" f"?ref={target_branch}",
                headers=self._headers(),
            )
            if head.status_code == 200:
                method = client.put
            else:
                method = client.post
            resp = await method(
                f"{self._api_base}/projects/{encoded_id}/repository/files/{encoded_path}",
                headers=self._headers(),
                json=payload,
            )
            if not resp.is_success:
                raise RepositoryError(f"GitLab write_file failed ({resp.status_code}): {resp.text}")

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        encoded_id = self._url_encode_id(repo_id)
        base = from_branch or await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._api_base}/projects/{encoded_id}/repository/branches",
                headers=self._headers(),
                params={"branch": new_branch, "ref": base},
            )
            if not resp.is_success:
                raise RepositoryError(f"GitLab create_branch failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (str) The repository's default branch name, or the configured/``"main"`` fallback.
        """
        encoded_id = self._url_encode_id(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._api_base}/projects/{encoded_id}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json().get("default_branch", self._default_branch_fallback)
        except Exception:
            pass
        return self._default_branch_fallback

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible to the configured token.

        If *org* is set, lists projects for that GitLab group.  Otherwise lists
        all projects the authenticated user is a member of.

        :param org: (str) Optional GitLab group name to list projects for.
        :return: (list) The accessible ``RepositoryInfo`` entries.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._api_base}/groups/{org}/projects?per_page=100"
            else:
                url = f"{self._api_base}/projects?membership=true&per_page=100"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return [_repo_info_from_gitlab(r) for r in resp.json()]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


def _repo_info_from_gitlab(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a GitLab API project object."""
    namespace = data.get("namespace", {}).get("full_path", "")
    name = data.get("name", "")
    identifier = f"{namespace}/{name}" if namespace else name
    return RepositoryInfo(
        identifier=identifier,
        name=name,
        description=data.get("description") or "",
        indexed=False,
    )
