"""Tests for the load_context_files tool."""

import pytest

from mcp_project_context_server.helpers.context_files import hash_content
from mcp_project_context_server.integrations.repository.registry import (
    reset_provider_for_testing as reset_repo,
)
from mcp_project_context_server.tools.load_context_files import handle


@pytest.fixture(autouse=True)
def reset_registries():
    reset_repo()
    yield
    reset_repo()


class TestLoadContextFiles:
    @pytest.mark.asyncio
    async def test_loads_requested_file_with_tagged_hash(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        result = await handle({"project_path": str(tmp_path), "files": ["project.md"]})

        assert len(result) == 1
        text = result[0].text
        assert text.startswith(f'<context-file path="project.md" sha512="{hash_content("# Project")}">')
        assert "# Project" in text
        assert text.endswith("</context-file>")

    @pytest.mark.asyncio
    async def test_missing_file_reports_not_found(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()

        result = await handle({"project_path": str(tmp_path), "files": ["nope.md"]})

        assert result[0].text == "File not found: nope.md"

    @pytest.mark.asyncio
    async def test_mixed_found_and_missing_preserves_order(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        result = await handle({"project_path": str(tmp_path), "files": ["project.md", "nope.md"]})

        assert len(result) == 2
        assert "project.md" in result[0].text
        assert result[1].text == "File not found: nope.md"

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo", "files": ["project.md"]})

        assert "not permitted" in result[0].text
        assert len(result) == 1
