"""Tests for the write_project tool."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.write_project import handle


class TestWriteProjectLocal:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_writes_new_project_md(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context").mkdir(parents=True)

        result = await handle({"project_path": str(project_dir), "content": "# Project\n\nHello."})

        project_md = project_dir / ".context" / "project.md"
        assert project_md.read_text(encoding="utf-8") == "# Project\n\nHello."
        assert "Updated project.md" in result[0].text
        assert "Run `index_project_context`" in result[0].text

    @pytest.mark.asyncio
    async def test_overwrites_existing_project_md(self, tmp_path):
        project_dir = tmp_path / "project"
        context_dir = project_dir / ".context"
        context_dir.mkdir(parents=True)
        (context_dir / "project.md").write_text("Old content.", encoding="utf-8")

        await handle({"project_path": str(project_dir), "content": "New content."})

        assert (context_dir / "project.md").read_text(encoding="utf-8") == "New content."

    @pytest.mark.asyncio
    async def test_no_context_dir(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        result = await handle({"project_path": str(project_dir), "content": "x"})

        assert "No .context/ directory found" in result[0].text

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo", "content": "x"})

        assert "not permitted" in result[0].text


class TestWriteProjectRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_write(self, monkeypatch):
        monkeypatch.setenv("REPO_ADR_WRITE_MODE", "direct")
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.get_default_branch = AsyncMock(return_value="main")

        with patch(
            "mcp_project_context_server.tools.write_project.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo", "content": "Remote content."})

        mock_provider.write_file.assert_called_once()
        args, kwargs = mock_provider.write_file.call_args
        assert args[1] == ".context/project.md"
        assert args[2] == "Remote content."
        assert "Wrote" in result[0].text
