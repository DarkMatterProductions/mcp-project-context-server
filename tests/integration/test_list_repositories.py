"""Integration tests — ``list_repositories`` tool.

The local filesystem provider (default) is used throughout.  No remote API
credentials or external services are required.

Scenarios covered:
- No ``PROJECT_PATH`` set → "No repositories found."
- ``PROJECT_PATH`` set to an existing directory → single repository entry.
- ``PROJECT_PATH`` set with ``org`` filter → ``org`` is accepted (ignored by
  local provider) and the response still lists the local repository.
- Invalid ``REPO_PROVIDER`` value → graceful error text.
- Response is always a single text content block.
"""
import pytest

from tests.integration.base import MCPIntegrationBase

_TOOL = "list_repositories"


class TestListRepositories(MCPIntegrationBase):

    # ------------------------------------------------------------------
    # No PROJECT_PATH configured
    # ------------------------------------------------------------------

    async def test_no_project_path_returns_no_repositories_found(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {})

        text = self.assert_tool_not_error(result)
        assert "No repositories found." == text

    # ------------------------------------------------------------------
    # PROJECT_PATH set — local provider lists it
    # ------------------------------------------------------------------

    async def test_project_path_returns_repository_entry(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()

        async with make_mcp_session({"PROJECT_PATH": str(project_dir)}) as session:
            result = await session.call_tool(_TOOL, {})

        text = self.assert_tool_not_error(result)
        assert str(project_dir) in text

    async def test_project_path_entry_shows_not_indexed_status(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "unindexed-project"
        project_dir.mkdir()

        async with make_mcp_session({"PROJECT_PATH": str(project_dir)}) as session:
            result = await session.call_tool(_TOOL, {})

        text = self.assert_tool_not_error(result)
        assert "not indexed" in text

    async def test_project_path_entry_uses_directory_name(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "cool-project-name"
        project_dir.mkdir()

        async with make_mcp_session({"PROJECT_PATH": str(project_dir)}) as session:
            result = await session.call_tool(_TOOL, {})

        text = self.assert_tool_not_error(result)
        assert "cool-project-name" in text

    # ------------------------------------------------------------------
    # org filter
    # ------------------------------------------------------------------

    async def test_org_filter_is_accepted_and_ignored_by_local_provider(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "org-project"
        project_dir.mkdir()

        async with make_mcp_session({"PROJECT_PATH": str(project_dir)}) as session:
            result = await session.call_tool(_TOOL, {"org": "my-org"})

        text = self.assert_tool_not_error(result)
        assert str(project_dir) in text

    async def test_org_filter_with_no_project_path_still_returns_no_repositories(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"org": "some-org"})

        text = self.assert_tool_not_error(result)
        assert "No repositories found." == text

    # ------------------------------------------------------------------
    # Invalid REPO_PROVIDER
    # ------------------------------------------------------------------

    async def test_invalid_repo_provider_returns_error_text(self, make_mcp_session):
        async with make_mcp_session({"REPO_PROVIDER": "unsupported_provider"}) as session:
            result = await session.call_tool(_TOOL, {})

        text = self.assert_tool_not_error(result)
        assert "Error listing repositories" in text
        assert "unsupported_provider" in text

    # ------------------------------------------------------------------
    # Response shape
    # ------------------------------------------------------------------

    async def test_response_is_single_text_content_block(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {})

        assert len(result.content) == 1
        assert result.content[0].type == "text"

    async def test_response_is_single_text_content_block_with_project_path(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "shape-test-project"
        project_dir.mkdir()

        async with make_mcp_session({"PROJECT_PATH": str(project_dir)}) as session:
            result = await session.call_tool(_TOOL, {})

        assert len(result.content) == 1
        assert result.content[0].type == "text"
