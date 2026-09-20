"""Tests for the read_adr_status tool."""
import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.read_adr_status import handle

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


class TestReadAdrStatus:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_returns_parsed_status(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "number_or_filename": 1})

        text = result[0].text
        assert "ADR-00001: First Decision" in text
        assert "Status: Accepted" in text

    @pytest.mark.asyncio
    async def test_legacy_format_message(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00002-legacy.md").write_text(_LEGACY, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "number_or_filename": 2})

        assert "legacy" in result[0].text.lower()
        assert "not supported" in result[0].text

    @pytest.mark.asyncio
    async def test_not_found(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context" / "decisions").mkdir(parents=True)

        result = await handle({"project_path": str(project_dir), "number_or_filename": 99})

        assert "No ADR found matching '99'" in result[0].text
