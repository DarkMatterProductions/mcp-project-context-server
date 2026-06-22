"""Integration tests — `save_session_summary` tool.

Tests cover:
- Error when `.context/` is absent.
- Creation of the `sessions/` sub-directory when it does not yet exist.
- Writing a new session file whose name matches today's date.
- Appending a timestamped block when called a second time on the same day.
- The response text containing the saved file path.

No external services (ChromaDB, Ollama) are required.
"""
from datetime import date
from pathlib import Path

import pytest

from tests.integration.base import MCPIntegrationBase

pytestmark = pytest.mark.asyncio

_TOOL = "save_session_summary"


class TestSaveSession(MCPIntegrationBase):

    # ------------------------------------------------------------------
    # Error paths
    # ------------------------------------------------------------------

    async def test_missing_context_dir_returns_error_text(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "no_context_here"
        project_dir.mkdir()

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "Some summary"},
            )

        text = self.assert_tool_not_error(result)
        assert "No .context/ directory found" in text

    # ------------------------------------------------------------------
    # New session
    # ------------------------------------------------------------------

    async def test_creates_sessions_directory_when_absent(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)
        sessions_dir = project_dir / ".context" / "sessions"
        assert not sessions_dir.exists()

        async with make_mcp_session() as session:
            await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "First ever session"},
            )

        assert sessions_dir.is_dir()

    async def test_new_session_file_uses_todays_date(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)
        today = date.today().strftime("%Y-%m-%d")

        async with make_mcp_session() as session:
            await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "Did some work"},
            )

        session_file = project_dir / ".context" / "sessions" / f"{today}.md"
        assert session_file.exists(), f"Expected session file at {session_file}"

    async def test_new_session_file_contains_summary_text(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)

        async with make_mcp_session() as session:
            await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "Implemented the feature"},
            )

        today = date.today().strftime("%Y-%m-%d")
        content = (project_dir / ".context" / "sessions" / f"{today}.md").read_text(encoding="utf-8")
        assert "Implemented the feature" in content

    async def test_new_session_file_has_date_header(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)
        today = date.today().strftime("%Y-%m-%d")

        async with make_mcp_session() as session:
            await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "Some work"},
            )

        content = (project_dir / ".context" / "sessions" / f"{today}.md").read_text(encoding="utf-8")
        assert f"# Session: {today}" in content

    async def test_response_contains_saved_file_path(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)
        today = date.today().strftime("%Y-%m-%d")

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "Finished the PR"},
            )

        text = self.assert_tool_not_error(result)
        assert "Session summary saved to" in text
        assert today in text
        assert "sessions" in text

    # ------------------------------------------------------------------
    # Append to existing session
    # ------------------------------------------------------------------

    async def test_appends_to_existing_session_file(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)
        today = date.today().strftime("%Y-%m-%d")

        session_file = project_dir / ".context" / "sessions"
        session_file.mkdir(parents=True, exist_ok=True)
        existing_file = session_file / f"{today}.md"
        existing_file.write_text(f"# Session: {today}\n\nFirst entry.", encoding="utf-8")

        async with make_mcp_session() as session:
            await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "Second entry appended"},
            )

        content = existing_file.read_text(encoding="utf-8")
        assert "First entry." in content
        assert "Second entry appended" in content

    async def test_appended_block_has_timestamp_heading(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)
        today = date.today().strftime("%Y-%m-%d")

        sessions_dir = project_dir / ".context" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        existing_file = sessions_dir / f"{today}.md"
        existing_file.write_text(f"# Session: {today}\n\nOriginal.", encoding="utf-8")

        async with make_mcp_session() as session:
            await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "Appended content"},
            )

        content = existing_file.read_text(encoding="utf-8")
        assert "### Session at" in content

    # ------------------------------------------------------------------
    # Response shape
    # ------------------------------------------------------------------

    async def test_response_is_single_text_content_block(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "summary": "Test summary"},
            )

        assert len(result.content) == 1
        assert result.content[0].type == "text"
