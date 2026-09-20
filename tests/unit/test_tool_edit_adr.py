"""Tests for the edit_adr tool."""
from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.edit_adr import handle

_WELL_FORMED = """# ADR-00001: First Decision

## Status
Accepted

## Context
Some context.

## Decision
We decided X.
"""


class TestEditAdrLocal:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_edits_section(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        adr_file = decisions_dir / "ADR-00001-first.md"
        adr_file.write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "section": "Context",
                "content": "Updated context.",
            }
        )

        content = adr_file.read_text(encoding="utf-8")
        assert "Updated context." in content
        assert "Some context." not in content
        assert "Updated section 'Context'" in result[0].text

    @pytest.mark.asyncio
    async def test_rejects_status_edit(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "section": "Status",
                "content": "Implemented",
            }
        )

        assert "update_adr_status" in result[0].text

    @pytest.mark.asyncio
    async def test_section_not_found(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "section": "Nonexistent",
                "content": "x",
            }
        )

        assert "No section named 'Nonexistent'" in result[0].text

    @pytest.mark.asyncio
    async def test_adr_not_found(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context" / "decisions").mkdir(parents=True)

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 99,
                "section": "Context",
                "content": "x",
            }
        )

        assert "No ADR found matching '99'" in result[0].text


class TestEditAdrRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_edit(self, monkeypatch):
        monkeypatch.setenv("REPO_ADR_WRITE_MODE", "direct")
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(
            return_value={"decisions/ADR-00001-first.md": _WELL_FORMED}
        )
        mock_provider.get_default_branch = AsyncMock(return_value="main")

        with (
            patch(
                "mcp_project_context_server.helpers.context_files.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.edit_adr.get_repository_provider",
                return_value=mock_provider,
            ),
        ):
            result = await handle(
                {
                    "project_path": "owner/repo",
                    "number_or_filename": 1,
                    "section": "Context",
                    "content": "Remote context.",
                }
            )

        mock_provider.write_file.assert_called_once()
        args, kwargs = mock_provider.write_file.call_args
        assert args[1] == ".context/decisions/ADR-00001-first.md"
        assert "Remote context." in args[2]
        assert "Wrote" in result[0].text
