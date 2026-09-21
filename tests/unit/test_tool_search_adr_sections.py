"""Tests for the search_adr_sections tool."""

from unittest.mock import AsyncMock, patch

import pytest
from mcp import types

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.search_adr_sections import handle

_WELL_FORMED = """# ADR-00001: First Decision

## Status
Accepted

## Context
Some context.
"""


class TestSearchAdrSections:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_adr_not_found_short_circuits_before_search(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context" / "decisions").mkdir(parents=True)

        with patch("mcp_project_context_server.tools.search_adr_sections.run_search") as mock_run_search:
            result = await handle({"project_path": str(project_dir), "number_or_filename": 99, "query": "q"})

        assert "No ADR found matching '99'" in result.content[0].text
        assert result.structured_content == {"results": []}
        mock_run_search.assert_not_called()

    @pytest.mark.asyncio
    async def test_delegates_to_run_search_with_exact_file(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00001-first.md").write_text(_WELL_FORMED, encoding="utf-8")

        fake_result = types.CallToolResult(
            content=[types.TextContent(type="text", text="hit")],
            structured_content={"results": [{"file": "decisions/ADR-00001-first.md", "content": "hit"}]},
        )
        with patch(
            "mcp_project_context_server.tools.search_adr_sections.run_search",
            new=AsyncMock(return_value=fake_result),
        ) as mock_run_search:
            result = await handle(
                {
                    "project_path": str(project_dir),
                    "number_or_filename": 1,
                    "query": "my query",
                    "n_results": 3,
                }
            )

        mock_run_search.assert_called_once_with(
            str(project_dir), "my query", 3, exact_file="decisions/ADR-00001-first.md"
        )
        assert result is fake_result

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo", "number_or_filename": 1, "query": "q"})

        assert "not permitted" in result.content[0].text
        assert result.structured_content == {"results": []}
