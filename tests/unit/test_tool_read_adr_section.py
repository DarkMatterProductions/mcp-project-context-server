"""Tests for the read_adr_section tool."""

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.read_adr_section import handle

_WELL_FORMED = """# ADR-00001: First Decision

## Status
Accepted

## Context
Some context.

## Decision
We decided X.
"""


class TestReadAdrSection:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_returns_section_with_heading(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "number_or_filename": 1, "section": "Decision"})

        text = result[0].text
        assert text.startswith("## Decision")
        assert "We decided X." in text
        assert "## Context" not in text

    @pytest.mark.asyncio
    async def test_section_not_found_lists_available(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        result = await handle({"project_path": str(project_dir), "number_or_filename": 1, "section": "Nonexistent"})

        text = result[0].text
        assert "No section named 'Nonexistent'" in text
        assert "Status" in text and "Context" in text and "Decision" in text

    @pytest.mark.asyncio
    async def test_adr_not_found(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context" / "decisions").mkdir(parents=True)

        result = await handle({"project_path": str(project_dir), "number_or_filename": 99, "section": "Decision"})

        assert "No ADR found matching '99'" in result[0].text
