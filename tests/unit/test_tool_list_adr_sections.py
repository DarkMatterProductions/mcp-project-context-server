"""Tests for the list_adr_sections tool."""
import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.list_adr_sections import handle

_WELL_FORMED = """# ADR-00001: First Decision

## Status
Accepted

## Context
Some context.

## Decision
We decided X.
"""


class TestListAdrSections:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_lists_sections_in_order(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "number_or_filename": 1})

        text = result[0].text
        assert "- Status" in text
        assert "- Context" in text
        assert "- Decision" in text
        assert text.index("- Status") < text.index("- Context") < text.index("- Decision")

    @pytest.mark.asyncio
    async def test_adr_not_found(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context" / "decisions").mkdir(parents=True)

        result = await handle({"project_path": str(project_dir), "number_or_filename": 99})

        assert "No ADR found matching '99'" in result[0].text
