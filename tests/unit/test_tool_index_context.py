import pytest

from mcp_project_context_server.tools.index_context import handle


class TestIndexContext:
    def setup_method(self):
        self.arguments = {"project_path": "/some/path"}

    @pytest.mark.asyncio
    async def test_index_context_calls_index_and_returns_result(self, mocker):
        mock_indexer = mocker.AsyncMock(return_value="Indexed 5 files.")
        mocker.patch(
            "mcp_project_context_server.tools.index_context.get_indexer",
            return_value=mock_indexer,
        )

        result = await handle(self.arguments)

        assert len(result) == 1
        assert result[0].text == "Indexed 5 files."
        mock_indexer.assert_called_once_with("/some/path")
