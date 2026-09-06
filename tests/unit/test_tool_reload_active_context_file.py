"""Tests for the reload_active_context_file tool."""

import pytest

from mcp_project_context_server.helpers.context_files import hash_content
from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing as reset_repo
from mcp_project_context_server.tools.reload_active_context_file import handle


@pytest.fixture(autouse=True)
def reset_registries():
    reset_repo()
    yield
    reset_repo()


class TestReloadActiveContextFile:
    @pytest.mark.asyncio
    async def test_unchanged_file_reports_no_change(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")
        known_hash = hash_content("# Project")

        result = await handle(
            {
                "project_path": str(tmp_path),
                "files": [{"path": "project.md", "known_sha512": known_hash}],
            }
        )

        assert result[0].text == "No change: project.md"

    @pytest.mark.asyncio
    async def test_changed_file_returns_fresh_tagged_block(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project v2", encoding="utf-8")

        result = await handle(
            {
                "project_path": str(tmp_path),
                "files": [{"path": "project.md", "known_sha512": "stale-hash"}],
            }
        )

        text = result[0].text
        expected_hash = hash_content("# Project v2")
        assert f'<context-file path="project.md" sha512="{expected_hash}">' in text
        assert "# Project v2" in text
        assert "discard the stale block" in text

    @pytest.mark.asyncio
    async def test_missing_file_reports_not_found(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()

        result = await handle(
            {
                "project_path": str(tmp_path),
                "files": [{"path": "nope.md", "known_sha512": "whatever"}],
            }
        )

        assert result[0].text == "File not found: nope.md"

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle(
            {
                "project_path": "unapproved-org/some-repo",
                "files": [{"path": "project.md", "known_sha512": "whatever"}],
            }
        )

        assert "not permitted" in result[0].text
        assert len(result) == 1
