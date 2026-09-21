"""Tests for the read_adr tool."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.helpers.context_files import hash_content
from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.read_adr import handle

_WELL_FORMED = """# ADR-00001: First Decision

## Status
Accepted

## Context
Some context.
"""


class TestReadAdrLocal:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_reads_by_number(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "number_or_filename": 1})

        text = result[0].text
        assert 'path="decisions/ADR-00001-first.md"' in text
        assert f'sha512="{hash_content(_WELL_FORMED)}"' in text
        assert "First Decision" in text

    @pytest.mark.asyncio
    async def test_reads_by_short_form(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "number_or_filename": "ADR-00001"})

        assert "First Decision" in result[0].text

    @pytest.mark.asyncio
    async def test_not_found(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context" / "decisions").mkdir(parents=True)

        result = await handle({"project_path": str(project_dir), "number_or_filename": 99})

        assert "No ADR found matching '99'" in result[0].text


class TestReadAdrRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_read(self):
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={"decisions/ADR-00001-first.md": _WELL_FORMED})

        with patch(
            "mcp_project_context_server.helpers.context_files.get_repository_provider",
            return_value=mock_provider,
        ):
            result = await handle({"project_path": "owner/repo", "number_or_filename": 1})

        assert "First Decision" in result[0].text
