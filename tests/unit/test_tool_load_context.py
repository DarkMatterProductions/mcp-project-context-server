from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.load_context import handle


class TestLoadContext:
    def setup_method(self):
        pass

    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_load_context_no_dir(self):
        arguments = {"project_path": "/nonexistent/path"}
        result = await handle(arguments)
        assert len(result) == 1
        assert "No .context/ directory found" in result[0].text

    @pytest.mark.asyncio
    async def test_load_context_full(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()

        (context_dir / "project.md").write_text("Main project", encoding="utf-8")

        decisions_dir = context_dir / "decisions"
        decisions_dir.mkdir()
        (decisions_dir / "001.md").write_text("Decision 1", encoding="utf-8")

        sessions_dir = context_dir / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "2026-01-01.md").write_text("Old Session", encoding="utf-8")
        (sessions_dir / "2026-01-02.md").write_text("New Session", encoding="utf-8")

        arguments = {"project_path": str(project_dir)}
        result = await handle(arguments)

        assert len(result) == 1
        text = result[0].text
        assert "## project.md" in text
        assert "Main project" in text
        assert "## Architecture Decisions" in text
        assert "001.md" in text
        assert "Decision 1" in text
        assert "## Last Session (2026-01-02)" in text
        assert "New Session" in text
        assert "Old Session" not in text  # Only the latest session

    @pytest.mark.asyncio
    async def test_load_context_blocked_by_allowlist(self, tmp_path, monkeypatch):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("Secret project", encoding="utf-8")

        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        arguments = {"project_path": "unapproved-org/some-repo"}
        result = await handle(arguments)

        assert "not permitted" in result[0].text
        assert "Secret project" not in result[0].text


class TestLoadContextRemote:
    @pytest.mark.asyncio
    async def test_no_context_files_returns_error(self):
        mock_provider = AsyncMock()
        mock_provider.fetch_context_files = AsyncMock(return_value={})

        with patch(
            "mcp_project_context_server.tools.load_context.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo"})

        assert "No .context/ directory found" in result[0].text

    @pytest.mark.asyncio
    async def test_full_load_from_flat_dict(self):
        files = {
            "project.md": "Main project",
            "decisions/001.md": "Decision 1",
            "sessions/2026-01-01.md": "Old Session",
            "sessions/2026-01-02.md": "New Session",
        }
        mock_provider = AsyncMock()
        mock_provider.fetch_context_files = AsyncMock(return_value=files)

        with patch(
            "mcp_project_context_server.tools.load_context.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo"})

        text = result[0].text
        assert "## project.md" in text
        assert "Main project" in text
        assert "## Architecture Decisions" in text
        assert "001.md" in text
        assert "Decision 1" in text
        assert "## Last Session (2026-01-02)" in text
        assert "New Session" in text
        assert "Old Session" not in text

    @pytest.mark.asyncio
    async def test_repository_error_is_reported(self):
        mock_provider = AsyncMock()
        mock_provider.fetch_context_files = AsyncMock(side_effect=RepositoryError("boom"))

        with patch(
            "mcp_project_context_server.tools.load_context.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo"})

        assert "Error accessing repository" in result[0].text
        assert "boom" in result[0].text
