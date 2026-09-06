"""Tests for the find_latest_session_file tool."""

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing as reset_repo
from mcp_project_context_server.tools.find_latest_session_file import handle


@pytest.fixture(autouse=True)
def reset_registries():
    reset_repo()
    yield
    reset_repo()


class TestFindLatestSessionFile:
    @pytest.mark.asyncio
    async def test_returns_most_recent_by_filename_sort(self, tmp_path):
        sessions_dir = tmp_path / ".context" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "2026-01-01.md").write_text("old", encoding="utf-8")
        (sessions_dir / "2026-03-15.md").write_text("newest", encoding="utf-8")
        (sessions_dir / "2026-02-10.md").write_text("middle", encoding="utf-8")

        result = await handle({"project_path": str(tmp_path)})

        assert result[0].text == "Latest session file: sessions/2026-03-15.md"

    @pytest.mark.asyncio
    async def test_no_sessions_dir_reports_none_found(self, tmp_path):
        (tmp_path / ".context").mkdir()

        result = await handle({"project_path": str(tmp_path)})

        assert result[0].text == "No session files found."

    @pytest.mark.asyncio
    async def test_no_context_dir_reports_none_found(self, tmp_path):
        result = await handle({"project_path": str(tmp_path)})

        assert result[0].text == "No session files found."

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo"})

        assert "not permitted" in result[0].text
        assert len(result) == 1
