"""Tests for the edit_project tool."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.edit_project import handle

_PROJECT_MD = """# Project

## Overview
Some overview.

## Goals
Some goals.
"""


class TestEditProjectLocal:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_edits_section(self, tmp_path):
        project_dir = tmp_path / "project"
        context_dir = project_dir / ".context"
        context_dir.mkdir(parents=True)
        project_md = context_dir / "project.md"
        project_md.write_text(_PROJECT_MD, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "section": "Goals", "content": "New goals."})

        content = project_md.read_text(encoding="utf-8")
        assert "New goals." in content
        assert "Some goals." not in content
        assert "Updated section 'Goals'" in result[0].text

    @pytest.mark.asyncio
    async def test_missing_project_md(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context").mkdir(parents=True)

        result = await handle({"project_path": str(project_dir), "section": "Goals", "content": "x"})

        assert "Could not read project.md" in result[0].text

    @pytest.mark.asyncio
    async def test_section_not_found(self, tmp_path):
        project_dir = tmp_path / "project"
        context_dir = project_dir / ".context"
        context_dir.mkdir(parents=True)
        (context_dir / "project.md").write_text(_PROJECT_MD, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "section": "Nonexistent", "content": "x"})

        assert "No section named 'Nonexistent' found in project.md" in result[0].text

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo", "section": "Goals", "content": "x"})

        assert "not permitted" in result[0].text


class TestEditProjectRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_edit(self, monkeypatch):
        monkeypatch.setenv("REPO_ADR_WRITE_MODE", "direct")
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={"project.md": _PROJECT_MD})
        mock_provider.get_default_branch = AsyncMock(return_value="main")

        with (
            patch(
                "mcp_project_context_server.helpers.context_files.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.edit_project.get_repository_provider",
                return_value=mock_provider,
            ),
        ):
            result = await handle({"project_path": "owner/repo", "section": "Goals", "content": "Remote goals."})

        mock_provider.write_file.assert_called_once()
        args, kwargs = mock_provider.write_file.call_args
        assert args[1] == ".context/project.md"
        assert "Remote goals." in args[2]
        assert "Wrote" in result[0].text
