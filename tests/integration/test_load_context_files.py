"""Integration tests — `load_context_files` tool.

No external services (ChromaDB, embedding providers) are required: this tool
only reads files off disk (or via the repository provider) and hashes their
contents.
"""

import pytest

from integration.base import MCPIntegrationBase

pytestmark = pytest.mark.asyncio

_TOOL = "load_context_files"


class TestLoadContextFiles(MCPIntegrationBase):

    async def test_loads_requested_file_with_tagged_hash(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path, project_md="# A project")

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "files": ["project.md"]},
            )

        text = self.assert_tool_not_error(result)
        assert '<context-file path="project.md" sha512="' in text
        assert "# A project" in text
        assert text.strip().endswith("</context-file>")

    async def test_loads_only_requested_decision_not_others(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(
            tmp_path,
            project_md="# A project",
            decisions={
                "0001-use-pgvector.md": "# ADR 1: use pgvector",
                "0002-use-fastapi.md": "# ADR 2: use fastapi",
            },
        )

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "files": ["decisions/0001-use-pgvector.md"]},
            )

        text = self.assert_tool_not_error(result)
        assert "decisions/0001-use-pgvector.md" in text
        assert "ADR 1" in text
        assert "ADR 2" not in text

    async def test_missing_file_reports_not_found(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path, project_md="# A project")

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "files": ["does-not-exist.md"]},
            )

        text = self.assert_tool_not_error(result)
        assert "File not found: does-not-exist.md" in text

    async def test_rejects_path_traversal(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path, project_md="# A project")
        secret = tmp_path / "secret.txt"
        secret.write_text("do not read me", encoding="utf-8")

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "files": ["../secret.txt"]},
            )

        text = self.assert_tool_not_error(result)
        assert "do not read me" not in text
        assert "File not found" in text
