"""Integration tests — server initialisation and tool registration.

These tests verify that:
- The MCP handshake completes successfully.
- All nine expected tools are registered with the server.
- Each tool exposes the correct input-schema shape (required fields present).
- Calling an unknown tool name returns a graceful error text rather than
  crashing the server.

No filesystem or external services are required.
"""

import pytest

from integration.base import MCPIntegrationBase

pytestmark = pytest.mark.asyncio

_EXPECTED_TOOLS = {
    "search_context_index",
    "search_adr_index",
    "search_session_files",
    "find_latest_session_file",
    "load_context_files",
    "reload_active_context_file",
    "save_session_summary",
    "index_project_context",
    "list_repositories",
}


class TestServerRegistration(MCPIntegrationBase):

    async def test_server_initialises_successfully(self, make_mcp_session):
        async with make_mcp_session() as session:
            assert session is not None

    async def test_all_tools_are_registered(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        registered = {t.name for t in result.tools}
        assert _EXPECTED_TOOLS == registered

    async def test_exactly_nine_tools_registered(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        assert len(result.tools) == 9

    @pytest.mark.parametrize("tool_name", sorted(_EXPECTED_TOOLS))
    async def test_each_tool_has_input_schema(self, make_mcp_session, tool_name):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next((t for t in result.tools if t.name == tool_name), None)
        assert tool is not None, f"Tool '{tool_name}' missing from registered tools"
        assert tool.input_schema is not None

    @pytest.mark.parametrize("tool_name", sorted({"search_context_index", "search_adr_index", "search_session_files"}))
    async def test_search_tools_have_output_schema(self, make_mcp_session, tool_name):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next((t for t in result.tools if t.name == tool_name), None)
        assert tool is not None, f"Tool '{tool_name}' missing from registered tools"
        assert tool.output_schema is not None
        assert "results" in tool.output_schema.get("required", [])

    async def test_search_context_index_requires_project_path_and_query(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "search_context_index")
        required = tool.input_schema.get("required", [])
        assert "project_path" in required
        assert "query" in required

    async def test_search_adr_index_requires_project_path_and_query(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "search_adr_index")
        required = tool.input_schema.get("required", [])
        assert "project_path" in required
        assert "query" in required

    async def test_search_session_files_requires_project_path_and_query(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "search_session_files")
        required = tool.input_schema.get("required", [])
        assert "project_path" in required
        assert "query" in required

    async def test_find_latest_session_file_requires_project_path(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "find_latest_session_file")
        assert "project_path" in tool.input_schema.get("required", [])

    async def test_load_context_files_requires_project_path_and_files(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "load_context_files")
        required = tool.input_schema.get("required", [])
        assert "project_path" in required
        assert "files" in required

    async def test_reload_active_context_file_requires_project_path_and_files(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "reload_active_context_file")
        required = tool.input_schema.get("required", [])
        assert "project_path" in required
        assert "files" in required

    async def test_save_session_summary_requires_project_path_and_summary(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "save_session_summary")
        required = tool.input_schema.get("required", [])
        assert "project_path" in required
        assert "summary" in required

    async def test_index_project_context_requires_project_path(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "index_project_context")
        assert "project_path" in tool.input_schema.get("required", [])

    async def test_list_repositories_has_no_required_fields(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.list_tools()
        tool = next(t for t in result.tools if t.name == "list_repositories")
        required = tool.input_schema.get("required", [])
        assert required == []

    async def test_unknown_tool_returns_error_text(self, make_mcp_session):
        async with make_mcp_session() as session:
            result = await session.call_tool("nonexistent_tool", {})
        text = self.get_tool_text(result)
        assert "nonexistent_tool" in text
