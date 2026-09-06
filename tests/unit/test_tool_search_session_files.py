"""Tests for the search_session_files tool."""

import pytest
from mcp import types

from mcp_project_context_server.tools.search_session_files import handle


class TestSearchSessionFiles:
    @pytest.mark.asyncio
    async def test_delegates_to_run_search_with_sessions_prefix(self, mocker):
        mock_run_search = mocker.patch(
            "mcp_project_context_server.tools.search_session_files.run_search",
            return_value=[types.TextContent(type="text", text="**[sessions/2026-01-01.md]**\nsnippet")],
        )

        result = await handle({"project_path": "/some/path", "query": "switch embedding providers", "n_results": 3})

        mock_run_search.assert_called_once_with("/some/path", "switch embedding providers", 3, file_prefix="sessions/")
        assert result[0].text == "**[sessions/2026-01-01.md]**\nsnippet"

    @pytest.mark.asyncio
    async def test_structured_content_passes_through_untouched(self, mocker):
        structured = {"results": [{"file": "sessions/2026-01-01.md", "chunk": None, "content": "snippet", "distance": None}]}
        mocker.patch(
            "mcp_project_context_server.tools.search_session_files.run_search",
            return_value=types.CallToolResult(
                content=[types.TextContent(type="text", text="**[sessions/2026-01-01.md]**\nsnippet")],
                structured_content=structured,
            ),
        )

        result = await handle({"project_path": "/some/path", "query": "switch embedding providers"})

        assert result.structured_content == structured

    @pytest.mark.asyncio
    async def test_defaults_n_results_to_five(self, mocker):
        mock_run_search = mocker.patch(
            "mcp_project_context_server.tools.search_session_files.run_search",
            return_value=[types.TextContent(type="text", text="ok")],
        )

        await handle({"project_path": "/some/path", "query": "q"})

        mock_run_search.assert_called_once_with("/some/path", "q", 5, file_prefix="sessions/")

    @pytest.mark.asyncio
    async def test_project_path_env_override(self, monkeypatch, mocker):
        monkeypatch.setenv("PROJECT_PATH", "/env/override")
        mock_run_search = mocker.patch(
            "mcp_project_context_server.tools.search_session_files.run_search",
            return_value=[types.TextContent(type="text", text="ok")],
        )

        await handle({"project_path": "/argument/path", "query": "q"})

        mock_run_search.assert_called_once_with("/env/override", "q", 5, file_prefix="sessions/")
