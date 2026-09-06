"""Tests for the GitLab repository provider."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.gitlab.client import GitLabRepositoryProvider


@pytest.fixture()
def provider(monkeypatch):
    monkeypatch.setenv("REPO_AUTH_TOKEN", "glpat-test")
    monkeypatch.setenv("REPO_BASE_URL", "https://gitlab.com")
    monkeypatch.setenv("REPO_DEFAULT_BRANCH", "main")
    return GitLabRepositoryProvider()


class TestNormaliseRepoId:
    """Tests for _normalise_repo_id in the GitLab provider."""

    def test_passthrough_namespace_project(self, provider):
        assert provider._normalise_repo_id("namespace/project") == "namespace/project"

    def test_normalises_https_url(self, provider):
        assert provider._normalise_repo_id("https://gitlab.com/owner/repo") == "owner/repo"

    def test_normalises_http_url(self, provider):
        assert provider._normalise_repo_id("http://gitlab.example.com/owner/repo") == "owner/repo"


class TestUrlEncodeId:
    """Tests for _url_encode_id."""

    def test_encodes_slash(self, provider):
        assert provider._url_encode_id("namespace/project") == "namespace%2Fproject"


class TestFetchContextFiles:
    """Tests for GitLabRepositoryProvider.fetch_context_files."""

    @pytest.mark.asyncio
    async def test_returns_empty_dict_on_404(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        tree_response = MagicMock()
        tree_response.status_code = 404
        tree_response.raise_for_status = MagicMock()

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
        tree_response.json.return_value = [
            {"type": "blob", "name": "project.md", "path": ".context/project.md"},
        ]

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


class TestWriteFile:
    """Tests for GitLabRepositoryProvider.write_file."""

    @pytest.mark.asyncio
    async def test_creates_file_when_not_exists(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        head_response = MagicMock()
        head_response.status_code = 404

        post_response = MagicMock()
        post_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=branch_response)
        mock_client.head = AsyncMock(return_value=head_response)
        mock_client.post = AsyncMock(return_value=post_response)
        mock_client.put = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.write_file("owner/repo", "README.md", "# Hello", "add readme")

        mock_client.post.assert_called_once()
        mock_client.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_updates_existing_file(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        head_response = MagicMock()
        head_response.status_code = 200

        put_response = MagicMock()
        put_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=branch_response)
        mock_client.head = AsyncMock(return_value=head_response)
        mock_client.put = AsyncMock(return_value=put_response)
        mock_client.post = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.write_file("owner/repo", "README.md", "# Updated", "update")

        mock_client.put.assert_called_once()
        mock_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_repository_error_on_failure(self, provider):
        branch_response = MagicMock()
        branch_response.status_code = 200
        branch_response.json.return_value = {"default_branch": "main"}

        head_response = MagicMock()
        head_response.status_code = 404

        post_response = MagicMock()
        post_response.is_success = False
        post_response.status_code = 400
        post_response.text = "Bad request"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=branch_response)
        mock_client.head = AsyncMock(return_value=head_response)
        mock_client.post = AsyncMock(return_value=post_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(RepositoryError, match="write_file failed"):
                await provider.write_file("owner/repo", "file.md", "x", "msg")

    @pytest.mark.asyncio
    async def test_explicit_branch_skips_default_branch_lookup(self, provider):
        head_response = MagicMock()
        head_response.status_code = 404

        post_response = MagicMock()
        post_response.is_success = True

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock()
        mock_client.head = AsyncMock(return_value=head_response)
        mock_client.post = AsyncMock(return_value=post_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            await provider.write_file("owner/repo", "README.md", "# Hello", "msg", branch="feature-x")

        mock_client.get.assert_not_called()
        head_url = mock_client.head.call_args[0][0]
        assert "ref=feature-x" in head_url
        post_kwargs = mock_client.post.call_args[1]
        assert post_kwargs["json"]["branch"] == "feature-x"


class TestCreateBranch:
    """Tests for GitLabRepositoryProvider.create_branch."""

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
        assert post_kwargs["params"] == {"branch": "new-feature", "ref": "main"}

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
        assert post_kwargs["params"] == {"branch": "new-feature", "ref": "develop"}

    @pytest.mark.asyncio
    async def test_raises_repository_error_on_failure(self, provider):
        create_response = MagicMock()
        create_response.is_success = False
        create_response.status_code = 400
        create_response.text = "Branch already exists"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=create_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(RepositoryError, match="create_branch failed"):
                await provider.create_branch("owner/repo", "new-feature", from_branch="develop")


class TestGetDefaultBranch:
    """Tests for GitLabRepositoryProvider.get_default_branch."""

    @pytest.mark.asyncio
    async def test_returns_default_branch_from_api(self, provider):
        api_response = MagicMock()
        api_response.status_code = 200
        api_response.json.return_value = {"default_branch": "dev"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=api_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            branch = await provider.get_default_branch("owner/repo")

        assert branch == "dev"


class TestListRepositories:
    """Tests for GitLabRepositoryProvider.list_repositories."""

    @pytest.mark.asyncio
    async def test_lists_group_projects(self, provider):
        api_response = MagicMock()
        api_response.raise_for_status = MagicMock()
        api_response.json.return_value = [
            {"name": "proj1", "description": "Desc", "namespace": {"full_path": "mygroup"}},
        ]

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=api_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            repos = await provider.list_repositories(org="mygroup")

        assert len(repos) == 1
        assert repos[0].name == "proj1"
        call_url = mock_client.get.call_args[0][0]
        assert "/groups/mygroup/projects" in call_url

    @pytest.mark.asyncio
    async def test_lists_member_projects_without_org(self, provider):
        api_response = MagicMock()
        api_response.raise_for_status = MagicMock()
        api_response.json.return_value = []

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=api_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            repos = await provider.list_repositories()

        call_url = mock_client.get.call_args[0][0]
        assert "membership=true" in call_url
