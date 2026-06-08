"""Tests for the list_repositories tool handler."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_project_context_server.integrations.repository.base import RepositoryInfo
from mcp_project_context_server.tools.list_repositories import handle


class TestListRepositoriesTool:
    """Tests for the list_repositories tool handle() function."""

    @pytest.mark.asyncio
    async def test_returns_formatted_list(self):
        repos = [
            RepositoryInfo(identifier="org/repo1", name="repo1", description="First repo", indexed=True, last_indexed="2024-01-15"),
            RepositoryInfo(identifier="org/repo2", name="repo2", description="", indexed=False),
        ]
        mock_provider = AsyncMock()
        mock_provider.list_repositories = AsyncMock(return_value=repos)

        with patch(
            "mcp_project_context_server.tools.list_repositories.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({})

        assert len(result) == 1
        text = result[0].text
        assert "org/repo1" in text
        assert "indexed" in text
        assert "last indexed: 2024-01-15" in text
        assert "org/repo2" in text
        assert "no description" in text

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
