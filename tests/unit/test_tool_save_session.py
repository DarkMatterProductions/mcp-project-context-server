from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.save_session import handle


class TestSaveSession:
    def setup_method(self):
        self.today = datetime.now().strftime("%Y-%m-%d")

    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_save_session_new(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()

        arguments = {"project_path": str(project_dir), "summary": "Initial work."}
        result = await handle(arguments)

        assert "Session summary saved" in result[0].text

        session_file = context_dir / "sessions" / f"{self.today}.md"
        assert session_file.exists()
        content = session_file.read_text(encoding="utf-8")
        assert f"# Session: {self.today}" in content
        assert "Initial work." in content

    @pytest.mark.asyncio
    async def test_save_session_append(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()
        sessions_dir = context_dir / "sessions"
        sessions_dir.mkdir()

        session_file = sessions_dir / f"{self.today}.md"
        session_file.write_text(f"# Session: {self.today}\n\nExisting part.", encoding="utf-8")

        arguments = {"project_path": str(project_dir), "summary": "Appended part."}
        await handle(arguments)

        content = session_file.read_text(encoding="utf-8")
        assert "Existing part." in content
        assert "Appended part." in content
        assert "### Session at" in content

    @pytest.mark.asyncio
    async def test_save_session_blocked_by_allowlist(self, tmp_path, monkeypatch):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()

        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        arguments = {"project_path": "unapproved-org/some-repo", "summary": "Sneaky write."}
        result = await handle(arguments)

        assert "not permitted" in result[0].text
        assert not (context_dir / "sessions").exists()


class TestSaveSessionRemote:
    def setup_method(self):
        self.today = datetime.now().strftime("%Y-%m-%d")

    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_direct_mode_writes_new_session(self):
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={})
        mock_provider.get_default_branch = AsyncMock(return_value="main")

        with patch(
            "mcp_project_context_server.tools.save_session.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo", "summary": "Did work"})

        mock_provider.write_file.assert_called_once()
        args, kwargs = mock_provider.write_file.call_args
        assert args[0] == "owner/repo"
        assert args[1] == f".context/sessions/{self.today}.md"
        assert "Did work" in args[2]
        assert kwargs["branch"] is None
        assert "Session summary saved" in result[0].text

    @pytest.mark.asyncio
    async def test_direct_mode_appends_to_existing_session(self):
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(
            return_value={f"sessions/{self.today}.md": f"# Session: {self.today}\n\nExisting part."}
        )
        mock_provider.get_default_branch = AsyncMock(return_value="main")

        with patch(
            "mcp_project_context_server.tools.save_session.get_repository_provider",
            return_value=mock_provider,
        ):
            await handle({"project_path": "owner/repo", "summary": "Appended part."})

        written_content = mock_provider.write_file.call_args[0][2]
        assert "Existing part." in written_content
        assert "Appended part." in written_content
        assert "### Session at" in written_content

    @pytest.mark.asyncio
    async def test_direct_mode_uses_configured_branch(self, monkeypatch):
        monkeypatch.setenv("REPO_SESSION_BRANCH", "session-notes")
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={})

        with patch(
            "mcp_project_context_server.tools.save_session.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo", "summary": "Did work"})

        args, kwargs = mock_provider.write_file.call_args
        assert kwargs["branch"] == "session-notes"
        mock_provider.get_default_branch.assert_not_called()
        assert "session-notes" in result[0].text

    @pytest.mark.asyncio
    async def test_branch_mode_creates_branch_and_reports_it(self, monkeypatch):
        monkeypatch.setenv("REPO_SESSION_WRITE_MODE", "branch")
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={})

        with patch(
            "mcp_project_context_server.tools.save_session.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo", "summary": "Did work"})

        mock_provider.create_branch.assert_called_once()
        branch_name = mock_provider.create_branch.call_args[0][1]
        assert branch_name.startswith(f"mcp-session/{self.today}-")

        args, kwargs = mock_provider.write_file.call_args
        assert kwargs["branch"] == branch_name
        assert branch_name in result[0].text

    @pytest.mark.asyncio
    async def test_fetch_error_is_reported(self):
        mock_provider = AsyncMock()
        mock_provider.fetch_context_files = AsyncMock(side_effect=RepositoryError("rate limited"))

        with patch(
            "mcp_project_context_server.tools.save_session.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo", "summary": "Did work"})

        assert "Error accessing repository" in result[0].text
        assert "rate limited" in result[0].text

    @pytest.mark.asyncio
    async def test_write_error_is_reported(self):
        mock_provider = AsyncMock()
        mock_provider.fetch_context_files = AsyncMock(return_value={})
        mock_provider.write_file = AsyncMock(side_effect=RepositoryError("push rejected"))
        mock_provider.get_default_branch = AsyncMock(return_value="main")

        with patch(
            "mcp_project_context_server.tools.save_session.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo", "summary": "Did work"})

        assert "Error saving session summary" in result[0].text
        assert "push rejected" in result[0].text
