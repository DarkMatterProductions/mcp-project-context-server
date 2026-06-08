"""Tests for the GitHub repository provider."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.github.client import (
    GitHubRepositoryProvider,
    _has_source_extension,
)


@pytest.fixture()
def provider(monkeypatch):
    monkeypatch.setenv("REPO_AUTH_TOKEN", "test-token")
    monkeypatch.setenv("REPO_BASE_URL", "https://api.github.com")
    monkeypatch.setenv("REPO_DEFAULT_BRANCH", "main")
    return GitHubRepositoryProvider()


class TestNormaliseRepoId:
    """Tests for _normalise_repo_id."""

    def test_passthrough_owner_repo(self, provider):
        assert provider._normalise_repo_id("owner/repo") == "owner/repo"

    def test_normalises_https_url(self, provider):
        assert provider._normalise_repo_id("https://github.com/owner/repo") == "owner/repo"

    def test_normalises_http_url(self, provider):
        assert provider._normalise_repo_id("http://github.example.com/owner/repo") == "owner/repo"

    def test_normalises_url_with_trailing_slash(self, provider):
        result = provider._normalise_repo_id("https://github.com/owner/repo/")
        # last two segments after stripping
        assert result == "owner/repo"


class TestFetchContextFiles:
    """Tests for GitHubRepositoryProvider.fetch_context_files."""

    @pytest.mark.asyncio
    async def test_returns_empty_dict_on_404(self, provider):
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await provider.fetch_context_files("owner/repo")

        assert result == {}

    @pytest.mark.asyncio
    async def test_returns_md_files_on_200(self, provider):
        listing_response = MagicMock()
        listing_response.status_code = 200
        listing_response.json.return_value = [
            {
                "type": "file",
                "name": "project.md",
                "path": ".context/project.md",
                "download_url": "https://raw.githubusercontent.com/owner/repo/main/.context/project.md",
            }
        ]

        raw_response = MagicMock()
        raw_response.status_code = 200
        raw_response.text = "# Project"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[listing_response, raw_response])

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await provider.fetch_context_files("owner/repo")

        assert "project.md" in result
        assert result["project.md"] == "# Project"


class TestWriteFile:
    """Tests for GitHubRepositoryProvider.write_file."""

    @pytest.mark.asyncio
    async def test_create_new_file(self, provider):
        check_response = MagicMock()
        check_response.status_code = 404

        put_response = MagicMock()
        put_response.status_code = 201
        put_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=check_response)
        mock_client.put = AsyncMock(return_value=put_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.write_file("owner/repo", "README.md", "# Hello", "add readme")

        mock_client.put.assert_called_once()
        call_kwargs = mock_client.put.call_args[1]
        assert "sha" not in call_kwargs["json"]

    @pytest.mark.asyncio
    async def test_update_existing_file(self, provider):
        check_response = MagicMock()
        check_response.status_code = 200
        check_response.json.return_value = {"sha": "abc123"}

        put_response = MagicMock()
        put_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=check_response)
        mock_client.put = AsyncMock(return_value=put_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.write_file("owner/repo", "README.md", "# Updated", "update readme")

        call_kwargs = mock_client.put.call_args[1]
        assert call_kwargs["json"]["sha"] == "abc123"

    @pytest.mark.asyncio
    async def test_raises_repository_error_on_failure(self, provider):
        check_response = MagicMock()
        check_response.status_code = 404

        put_response = MagicMock()
        put_response.is_success = False
        put_response.status_code = 422
        put_response.text = "Validation failed"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=check_response)
        mock_client.put = AsyncMock(return_value=put_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(RepositoryError, match="write_file failed"):
                await provider.write_file("owner/repo", "bad.md", "x", "msg")


class TestGetDefaultBranch:
    """Tests for GitHubRepositoryProvider.get_default_branch."""

    @pytest.mark.asyncio
    async def test_returns_default_branch_from_api(self, provider):
        api_response = MagicMock()
        api_response.status_code = 200
        api_response.json.return_value = {"default_branch": "develop"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=api_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            branch = await provider.get_default_branch("owner/repo")

        assert branch == "develop"

    @pytest.mark.asyncio
    async def test_falls_back_to_env_on_failure(self, monkeypatch):
        monkeypatch.setenv("REPO_DEFAULT_BRANCH", "fallback-branch")
        p = GitHubRepositoryProvider()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=Exception("network error"))

        with patch("httpx.AsyncClient", return_value=mock_client):
            branch = await p.get_default_branch("owner/repo")

        assert branch == "fallback-branch"


class TestListRepositories:
    """Tests for GitHubRepositoryProvider.list_repositories."""

    @pytest.mark.asyncio
    async def test_lists_org_repos(self, provider):
        api_response = MagicMock()
        api_response.status_code = 200
        api_response.raise_for_status = MagicMock()
        api_response.json.return_value = [
            {"full_name": "myorg/repo1", "name": "repo1", "description": "First repo"},
        ]

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=api_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            repos = await provider.list_repositories(org="myorg")

        assert len(repos) == 1
        assert repos[0].identifier == "myorg/repo1"
        call_url = mock_client.get.call_args[0][0]
        assert "/orgs/myorg/repos" in call_url

    @pytest.mark.asyncio
    async def test_lists_user_repos_without_org(self, provider):
        api_response = MagicMock()
        api_response.status_code = 200
        api_response.raise_for_status = MagicMock()
        api_response.json.return_value = [
            {"full_name": "user/my-repo", "name": "my-repo", "description": None},
        ]

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=api_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            repos = await provider.list_repositories()

        assert len(repos) == 1
        call_url = mock_client.get.call_args[0][0]
        assert "/user/repos" in call_url
