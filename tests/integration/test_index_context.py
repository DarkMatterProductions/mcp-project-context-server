"""Integration tests — ``index_project_context`` tool.

The "no .context/ directory" error path is exercised without any external
services.  All remaining tests require a running ChromaDB instance and an
embedding provider (Ollama by default) and are marked
``pytest.mark.external_services``.

Run only tests that require no external services:
    pytest tests/integration/test_index_context.py -v -m "not external_services"
"""
import pytest

from tests.integration.base import MCPIntegrationBase

pytestmark = pytest.mark.asyncio

_TOOL = "index_project_context"


class TestIndexContextErrors(MCPIntegrationBase):
    """Error-path tests that require no external services."""

    async def test_missing_context_dir_returns_error_text(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "no_context_here"
        project_dir.mkdir()

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "No .context/ directory found" in text

    async def test_response_is_single_text_content_block_on_error(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "no_context"
        project_dir.mkdir()

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        assert len(result.content) == 1
        assert result.content[0].type == "text"


@pytest.mark.external_services
class TestIndexContextWithExternalServices(MCPIntegrationBase):
    """Tests that require a running ChromaDB and embedding provider (Ollama by default).

    Skip with: pytest -m "not external_services"
    """

    async def test_empty_context_dir_indexes_zero_chunks(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path)

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "Indexed 0 chunks" in text

    async def test_project_md_is_indexed_and_summary_returned(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path, project_md="# Indexed Project\n\nSome content here.")

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "Indexed" in text
        assert "chunks" in text

    async def test_index_then_search_returns_results(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(
            tmp_path,
            project_md="# Chromadb Decision\n\nWe chose ChromaDB because it is embeddable.",
        )

        async with make_mcp_session() as session:
            await session.call_tool(_TOOL, {"project_path": str(project_dir)})
            search_result = await session.call_tool(
                "search_project_context",
                {"project_path": str(project_dir), "query": "ChromaDB vector store", "n_results": 1},
            )

        text = self.assert_tool_not_error(search_result)
        assert "ChromaDB" in text
