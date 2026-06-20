"""Integration tests — ``load_project_context`` tool.

Tests cover the full range of valid filesystem layouts that the tool supports
as well as the expected error response when no ``.context/`` directory exists.

No external services (ChromaDB, Ollama) are required.
"""

from tests.integration.base import MCPIntegrationBase

_TOOL = "load_project_context"


class TestLoadContext(MCPIntegrationBase):

    # ------------------------------------------------------------------
    # Error paths
    # ------------------------------------------------------------------

    async def test_missing_context_dir_returns_error_text(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "no_context_here"
        project_dir.mkdir()

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "No .context/ directory found" in text

    async def test_empty_context_dir_returns_no_files_message(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "No context files found." in text

    # ------------------------------------------------------------------
    # project.md
    # ------------------------------------------------------------------

    async def test_loads_project_md_content(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path, project_md="# My Project\n\nProject overview here.")

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "## project.md" in text
        assert "My Project" in text
        assert "Project overview here." in text

    # ------------------------------------------------------------------
    # Architecture decisions
    # ------------------------------------------------------------------

    async def test_loads_decisions_directory(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(
            tmp_path,
            decisions={"ADR-00001-use-chromadb.md": "# ADR-00001\n\nUse ChromaDB for vector storage."},
        )

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "## Architecture Decisions" in text
        assert "ADR-00001-use-chromadb.md" in text
        assert "Use ChromaDB for vector storage." in text

    async def test_loads_multiple_decisions_in_sorted_order(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(
            tmp_path,
            decisions={
                "ADR-00002-embedding.md": "Decision 2",
                "ADR-00001-storage.md": "Decision 1",
            },
        )

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        pos_adr1 = text.index("ADR-00001")
        pos_adr2 = text.index("ADR-00002")
        assert pos_adr1 < pos_adr2, "ADRs should appear in sorted (alphabetical) order"

    # ------------------------------------------------------------------
    # Session summaries
    # ------------------------------------------------------------------

    async def test_loads_only_the_latest_session(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(
            tmp_path,
            sessions={
                "2025-01-01.md": "Old session content",
                "2025-06-20.md": "Latest session content",
                "2025-03-15.md": "Middle session content",
            },
        )

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "Latest session content" in text
        assert "Old session content" not in text
        assert "Middle session content" not in text

    async def test_latest_session_heading_contains_file_stem(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(
            tmp_path,
            sessions={"2025-06-20.md": "Session body"},
        )

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "## Last Session (2025-06-20)" in text

    # ------------------------------------------------------------------
    # Full project — all content types present
    # ------------------------------------------------------------------

    async def test_full_project_includes_all_sections(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(
            tmp_path,
            project_md="# Full Project",
            decisions={"ADR-00001-choice.md": "An architectural choice."},
            sessions={"2025-06-20.md": "Worked on integration tests."},
        )

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "## project.md" in text
        assert "Full Project" in text
        assert "## Architecture Decisions" in text
        assert "An architectural choice." in text
        assert "## Last Session" in text
        assert "Worked on integration tests." in text

    async def test_project_md_only_no_decisions_section(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path, project_md="# Solo project")

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "## project.md" in text
        assert "## Architecture Decisions" not in text
        assert "## Last Session" not in text

    async def test_response_is_single_text_content_block(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path, project_md="# Test")

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        assert len(result.content) == 1
        assert result.content[0].type == "text"
