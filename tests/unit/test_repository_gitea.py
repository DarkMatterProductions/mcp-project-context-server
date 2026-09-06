"""Tests for the Gitea repository provider."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.gitea.client import GiteaRepositoryProvider


@pytest.fixture()
def provider(monkeypatch):
    monkeypatch.setenv("REPO_AUTH_TOKEN", "gitea-token")
    monkeypatch.setenv("REPO_BASE_URL", "https://gitea.example.com")
    monkeypatch.setenv("REPO_DEFAULT_BRANCH", "main")
    return GiteaRepositoryProvider()


class TestInit:
    """Tests for GiteaRepositoryProvider.__init__."""

    def test_raises_environment_error_when_base_url_not_set(self, monkeypatch):
        monkeypatch.delenv("REPO_BASE_URL", raising=False)
        with pytest.raises(EnvironmentError, match="REPO_BASE_URL is required"):
            GiteaRepositoryProvider()

    def test_creates_provider_when_base_url_set(self, monkeypatch):
        monkeypatch.setenv("REPO_BASE_URL", "https://gitea.example.com")
        p = GiteaRepositoryProvider()
        assert p is not None


class TestNormaliseRepoId:
    """Tests for _normalise_repo_id in the Gitea provider."""

    def test_passthrough_owner_repo(self, provider):
        assert provider._normalise_repo_id("owner/repo") == "owner/repo"

    def test_normalises_https_url(self, provider):
        assert provider._normalise_repo_id("https://gitea.example.com/owner/repo") == "owner/repo"

    def test_normalises_http_url(self, provider):
        assert provider._normalise_repo_id("http://gitea.example.com/owner/repo") == "owner/repo"


class TestFetchContextFiles:
    """Tests for GiteaRepositoryProvider.fetch_context_files."""

    @pytest.mark.asyncio
    async def test_returns_empty_dict_on_404(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        tree_response = MagicMock()
        tree_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[branch_response, tree_response])

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await provider.fetch_context_files("owner/repo")

        assert result == {}

    @pytest.mark.asyncio
    async def test_returns_md_files_on_200(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        tree_response = MagicMock()
        tree_response.status_code = 200
        tree_response.raise_for_status = MagicMock()
        tree_response.json.return_value = {
            "tree": [
                {"path": ".context/project.md", "type": "blob"},
            ]
        }

        raw_response = MagicMock()
        raw_response.status_code = 200
        raw_response.text = "# Project"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[branch_response, tree_response, raw_response])

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await provider.fetch_context_files("owner/repo")

        assert "project.md" in result
        assert result["project.md"] == "# Project"


class TestFetchSourceBundle:
    """Tests for GiteaRepositoryProvider.fetch_source_bundle."""

    @pytest.mark.asyncio
    async def test_returns_none_on_non_200(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        bundle_response = MagicMock()
        bundle_response.status_code = 404

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[branch_response, bundle_response])

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await provider.fetch_source_bundle("owner/repo")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_content_on_200(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        bundle_response = MagicMock()
        bundle_response.status_code = 200
        bundle_response.text = "# Bundle"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[branch_response, bundle_response])

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await provider.fetch_source_bundle("owner/repo")

        assert result == "# Bundle"


class TestWriteFile:
    """Tests for GiteaRepositoryProvider.write_file."""

    @pytest.mark.asyncio
    async def test_creates_new_file(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        check_response = MagicMock()
        check_response.status_code = 404

        post_response = MagicMock()
        post_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[branch_response, check_response])
        mock_client.post = AsyncMock(return_value=post_response)
        mock_client.patch = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.write_file("owner/repo", "file.md", "content", "msg")

        mock_client.post.assert_called_once()
        mock_client.patch.assert_not_called()

    @pytest.mark.asyncio
    async def test_updates_existing_file(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        check_response = MagicMock()
        check_response.status_code = 200
        check_response.json.return_value = {"sha": "sha123"}

        patch_response = MagicMock()
        patch_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[branch_response, check_response])
        mock_client.patch = AsyncMock(return_value=patch_response)
        mock_client.post = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.write_file("owner/repo", "file.md", "updated", "update msg")

        mock_client.patch.assert_called_once()
        mock_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_repository_error_on_failure(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        check_response = MagicMock()
        check_response.status_code = 404

        post_response = MagicMock()
        post_response.is_success = False
        post_response.status_code = 500
        post_response.text = "Server error"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=[branch_response, check_response])
        mock_client.post = AsyncMock(return_value=post_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(RepositoryError, match="write_file failed"):
                await provider.write_file("owner/repo", "file.md", "x", "msg")

    @pytest.mark.asyncio
    async def test_explicit_branch_skips_default_branch_lookup(self, provider):
        check_response = MagicMock()
        check_response.status_code = 404

        post_response = MagicMock()
        post_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=check_response)
        mock_client.post = AsyncMock(return_value=post_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.write_file("owner/repo", "file.md", "content", "msg", branch="feature-x")

        # Only one GET (the SHA check, scoped to the given branch) — no
        # default-branch lookup needed since branch was given explicitly.
        assert mock_client.get.call_count == 1
        check_kwargs = mock_client.get.call_args[1]
        assert check_kwargs["params"] == {"ref": "feature-x"}
        post_kwargs = mock_client.post.call_args[1]
        assert post_kwargs["json"]["branch"] == "feature-x"


class TestCreateBranch:
    """Tests for GiteaRepositoryProvider.create_branch."""

    @pytest.mark.asyncio
    async def test_creates_branch_from_default(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        create_response = MagicMock()
        create_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=branch_response)
        mock_client.post = AsyncMock(return_value=create_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.create_branch("owner/repo", "new-feature")

        mock_client.post.assert_called_once()
        post_kwargs = mock_client.post.call_args[1]
        assert post_kwargs["json"] == {"new_branch_name": "new-feature", "old_branch_name": "main"}

    @pytest.mark.asyncio
    async def test_creates_branch_from_explicit_base(self, provider):
        create_response = MagicMock()
        create_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock()
        mock_client.post = AsyncMock(return_value=create_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.create_branch("owner/repo", "new-feature", from_branch="develop")

        mock_client.get.assert_not_called()
        post_kwargs = mock_client.post.call_args[1]
        assert post_kwargs["json"] == {"new_branch_name": "new-feature", "old_branch_name": "develop"}

    @pytest.mark.asyncio
    async def test_raises_repository_error_on_failure(self, provider):
        create_response = MagicMock()
        create_response.is_success = False
        create_response.status_code = 409
        create_response.text = "Branch already exists"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=create_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(RepositoryError, match="create_branch failed"):
                await provider.create_branch("owner/repo", "new-feature", from_branch="develop")


class TestGetDefaultBranch:
    """Tests for GiteaRepositoryProvider.get_default_branch."""

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
    async def test_falls_back_on_error(self, provider):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=Exception("network error"))

        with patch("httpx.AsyncClient", return_value=mock_client):
            branch = await provider.get_default_branch("owner/repo")

        assert branch == "main"


class TestListRepositories:
    """Tests for GiteaRepositoryProvider.list_repositories."""

    @pytest.mark.asyncio
    async def test_lists_org_repos(self, provider):
        api_response = MagicMock()
        api_response.raise_for_status = MagicMock()
        api_response.json.return_value = [
            {"full_name": "myorg/repo1", "name": "repo1", "description": "A repo"},
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
    async def test_searches_repos_without_org(self, provider):
        api_response = MagicMock()
        api_response.raise_for_status = MagicMock()
        api_response.json.return_value = {
            "data": [
                {"full_name": "user/proj", "name": "proj", "description": ""},
            ]
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=api_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            repos = await provider.list_repositories()

        assert len(repos) == 1
        call_url = mock_client.get.call_args[0][0]
        assert "/repos/search" in call_url
