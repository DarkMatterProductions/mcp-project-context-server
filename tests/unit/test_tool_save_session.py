from datetime import datetime

import pytest

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
