import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.index_context import handle


class TestIndexContext:
    def setup_method(self):
        self.arguments = {"project_path": "/some/path"}

    def teardown_method(self):
        reset_provider_for_testing()

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

    @pytest.mark.asyncio
    async def test_index_context_blocked_by_allowlist(self, mocker, monkeypatch):
        mock_get_indexer = mocker.patch(
            "mcp_project_context_server.tools.index_context.get_indexer",
        )

        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo"})

        assert "not permitted" in result[0].text
        mock_get_indexer.assert_not_called()
