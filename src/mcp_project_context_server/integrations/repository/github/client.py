"""GitHub repository provider implementation using the GitHub REST API."""

import base64
import logging
import os
from typing import Optional

import httpx

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    normalize_repo_identifier,
)

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GitHubRepositoryProvider:
    """Repository provider that communicates with the GitHub REST API.

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — GitHub personal access token (required for private repos).
    * ``REPO_BASE_URL`` — Base URL for GitHub Enterprise (default: ``https://api.github.com``).
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name when the API cannot be reached
      (default: ``"main"``).
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables."""
        self._token: str = os.getenv("GITHUB_TOKEN", "")
        self._base_url: str = os.getenv("REPO_BASE_URL", "https://api.github.com").rstrip("/")
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "github"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to the ``owner/repo`` form.

        If *repo_id* starts with ``http://`` or ``https://`` the last two path
        segments are extracted and joined.  Otherwise the value is returned as-is.
        """
        return normalize_repo_identifier(repo_id)

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for GitHub API requests."""
        headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _split(self, repo_id: str) -> tuple[str, str]:
        """Return *(owner, repo)* from a normalised ``owner/repo`` string."""
        owner, repo = self._normalise_repo_id(repo_id).split("/", 1)
        return owner, repo

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` directory of the repository.

        Returns an empty dict on 404.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/.context",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            items = resp.json()
            await _collect_github_md_files(client, items, self._headers(), ".context", result)
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        owner, repo = self._split(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/.context/BUNDLE.md",
                headers=self._headers(),
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            download_url = data.get("download_url")
            if not download_url:
                return None
            raw = await client.get(download_url, headers=self._headers())
            return raw.text

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files via the Git Trees API.

        Capped at 200 files.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            candidates = [
                item for item in tree if item.get("type") == "blob" and _has_source_extension(item.get("path", ""))
            ][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                raw_resp = await client.get(
                    f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                )
                if raw_resp.status_code == 200:
                    data = raw_resp.json()
                    if data.get("encoding") == "base64":
                        result[path] = base64.b64decode(data["content"].replace("\n", "")).decode(
                            "utf-8", errors="replace"
                        )
        return result

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Create or update *path* in the repository.

        Writes to *branch* if given, otherwise the repository's default
        branch.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param path: (str) The file path to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        owner, repo = self._split(repo_id)
        target_branch = branch or await self.get_default_branch(repo_id)
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        async with httpx.AsyncClient() as client:
            # Check for existing file SHA on the target branch specifically —
            # without ?ref= this would always read the default branch's SHA,
            # which is wrong once writes can target other branches.
            sha: Optional[str] = None
            check = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                params={"ref": target_branch},
            )
            if check.status_code == 200:
                sha = check.json().get("sha")

            payload: dict = {"message": message, "content": encoded, "branch": target_branch}
            if sha:
                payload["sha"] = sha

            resp = await client.put(
                f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                json=payload,
            )
            if not resp.is_success:
                raise RepositoryError(f"GitHub write_file failed ({resp.status_code}): {resp.text}")

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* pointing at the tip of *from_branch* (or the default branch).

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the base ref cannot be resolved or the
            API returns a non-success status when creating the new ref.
        """
        owner, repo = self._split(repo_id)
        base = from_branch or await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            ref_resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/git/ref/heads/{base}",
                headers=self._headers(),
            )
            if not ref_resp.is_success:
                raise RepositoryError(
                    f"GitHub create_branch failed to resolve base branch '{base}' "
                    f"({ref_resp.status_code}): {ref_resp.text}"
                )
            sha = ref_resp.json()["object"]["sha"]

            resp = await client.post(
                f"{self._base_url}/repos/{owner}/{repo}/git/refs",
                headers=self._headers(),
                json={"ref": f"refs/heads/{new_branch}", "sha": sha},
            )
            if not resp.is_success:
                raise RepositoryError(f"GitHub create_branch failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The repository's default branch name, or the configured/``"main"`` fallback.
        """
        owner, repo = self._split(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._base_url}/repos/{owner}/{repo}",
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
        lists the authenticated user's repositories.

        :param org: (str) Optional organisation name to list repositories for.
        :return: (list) The accessible ``RepositoryInfo`` entries.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._base_url}/orgs/{org}/repos?per_page=100"
            else:
                url = f"{self._base_url}/user/repos?per_page=100"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return [_repo_info_from_github(r) for r in resp.json()]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


async def _collect_github_md_files(
    client: httpx.AsyncClient,
    items: list,
    headers: dict,
    prefix: str,
    result: dict,
) -> None:
    """Recursively collect .md files from a GitHub contents listing."""
    for item in items:
        if item.get("type") == "file" and item["name"].endswith(".md"):
            download_url = item.get("download_url")
            if download_url:
                raw = await client.get(download_url, headers=headers)
                if raw.status_code == 200:
                    rel_path = item["path"].removeprefix(prefix + "/")
                    result[rel_path] = raw.text
        elif item.get("type") == "dir":
            sub = await client.get(item["url"], headers=headers)
            if sub.status_code == 200:
                await _collect_github_md_files(client, sub.json(), headers, prefix, result)


def _repo_info_from_github(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a GitHub API repository object."""
    return RepositoryInfo(
        identifier=data.get("full_name", ""),
        name=data.get("name", ""),
        description=data.get("description") or "",
        indexed=False,
    )
