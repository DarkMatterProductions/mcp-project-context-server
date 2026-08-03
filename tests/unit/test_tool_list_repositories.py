"""Tests for the list_repositories tool handler."""
import re
from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import TextContent

from mcp_project_context_server.integrations.repository.base import RepositoryInfo
from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.list_repositories import handle


class TestListRepositoriesTool:
    """Tests for the list_repositories tool handle() function."""

    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_returns_formatted_list(self):
        pattern = re.compile(r"org/repo[0-9]+")
        repos_def = {
            "org/repo1": {
                "identifier": "org/repo1",
                "name": "repo1",
                "indexed": True,
                "last_indexed": "2024-01-15",
                "description": "First repo",
            },
            "org/repo2": {
                "identifier": "org/repo2",
                "name": "repo2",
                "indexed": False,
                "last_indexed": None,
                "description": "",
            }
        }
        repos = [
            RepositoryInfo(
                identifier=repo_details["identifier"], name=repo_details["name"], description=repo_details["description"], indexed=repo_details["indexed"], last_indexed=repo_details["last_indexed"]
            ) for repo_id, repo_details in repos_def.items()
        ]
        mock_provider = AsyncMock()
        mock_provider.list_repositories = AsyncMock(return_value=repos)

        with patch(
            "mcp_project_context_server.tools.list_repositories.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({})

        assert len(result.content) == 2
        for content in result.content:
            assert type(content) is TextContent
            text = content.text
            _id = pattern.search(text).group(0)
            assert repos_def[_id]["identifier"] in text
            if repos_def[_id]["description"] is not None and repos_def[_id]["description"] is not "":
                assert repos_def[_id]["description"] in text
            if repos_def[_id]["indexed"]:
                assert "indexed" in text
                assert f"last indexed: {repos_def[_id]['last_indexed']}" in text

    @pytest.mark.asyncio
    async def test_returns_no_repositories_found_for_empty_list(self):
        mock_provider = AsyncMock()
        mock_provider.list_repositories = AsyncMock(return_value=[])

        with patch(
            "mcp_project_context_server.tools.list_repositories.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({})

        assert len(result) == 1
        assert result[0].text == "No repositories found."

    @pytest.mark.asyncio
    async def test_returns_error_message_on_exception(self):
        with patch(
            "mcp_project_context_server.tools.list_repositories.get_repository_provider",
            side_effect=Exception("Provider not configured"),
        ):
            result = await handle({})

        assert len(result) == 1
        assert "Error listing repositories" in result[0].text
        assert "Provider not configured" in result[0].text

    @pytest.mark.asyncio
    async def test_passes_org_to_provider(self):
        mock_provider = AsyncMock()
        mock_provider.list_repositories = AsyncMock(return_value=[])

        with patch(
            "mcp_project_context_server.tools.list_repositories.get_repository_provider",
            return_value=mock_provider,
        ):
            await handle({"org": "myorg"})

        mock_provider.list_repositories.assert_called_once_with(org="myorg")

    @pytest.mark.asyncio
    async def test_filters_out_repos_not_in_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        repos = [
            RepositoryInfo(identifier="approved-org/repo1", name="repo1", description="", indexed=True),
            RepositoryInfo(identifier="unapproved-org/repo2", name="repo2", description="", indexed=False),
        ]
        mock_provider = AsyncMock()
        mock_provider.list_repositories = AsyncMock(return_value=repos)

        with patch(
            "mcp_project_context_server.tools.list_repositories.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({})

        text = result.structuredContent
        assert "approved-org/repo1" in text
        assert "unapproved-org/repo2" not in text
