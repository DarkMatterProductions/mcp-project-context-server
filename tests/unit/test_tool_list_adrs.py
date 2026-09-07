"""Tests for the list_adrs tool."""
from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.list_adrs import handle

_WELL_FORMED = """# ADR-00001: First Decision

## Status
Accepted

## Context
Some context.
"""

_LEGACY = """# ADR-00002: Legacy Decision

**Status:** Accepted

Legacy body.
"""


class TestListAdrsLocal:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_no_adrs(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context").mkdir(parents=True)

        result = await handle({"project_path": str(project_dir)})

        assert "No ADRs found" in result[0].text

    @pytest.mark.asyncio
    async def test_formats_table(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle({"project_path": str(project_dir)})

        text = result[0].text
        assert "| ADR-00001 | First Decision | Accepted | ADR-00001-first.md |" in text

    @pytest.mark.asyncio
    async def test_legacy_status_reported_as_unparsed(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00002-legacy.md").write_text(_LEGACY, encoding="utf-8")

        result = await handle({"project_path": str(project_dir)})

        assert "_(unparsed" in result[0].text

    @pytest.mark.asyncio
    async def test_warnings_appended_for_bad_filenames(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "not-an-adr.md").write_text("# Not an ADR\n", encoding="utf-8")

        result = await handle({"project_path": str(project_dir)})

        assert "**Warnings:**" in result[0].text
        assert "not-an-adr.md" in result[0].text

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo"})

        assert "not permitted" in result[0].text


class TestListAdrsRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_empty(self):
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={})

        with patch(
            "mcp_project_context_server.helpers.context_files.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo"})

        assert "No ADRs found" in result[0].text

    @pytest.mark.asyncio
    async def test_remote_lists_adrs(self):
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(
            return_value={"decisions/ADR-00001-first.md": _WELL_FORMED}
        )

        with patch(
            "mcp_project_context_server.helpers.context_files.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo"})

        assert "ADR-00001" in result[0].text
        assert "First Decision" in result[0].text
