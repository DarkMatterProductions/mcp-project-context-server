import pytest

from mcp_project_context_server.tools.search_context import handle


class TestSearchContext:
    def setup_method(self):
        pass

    @pytest.mark.asyncio
    async def test_search_context_no_dir(self):
        arguments = {"project_path": "/nonexistent", "query": "test"}
        result = await handle(arguments)
        assert "No .context/ directory found" in result[0].text

    @pytest.mark.asyncio
    async def test_search_context_success(self, tmp_path, mocker):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        arguments = {"project_path": str(project_dir), "query": "my query", "n_results": 2}

        mock_collection = mocker.MagicMock()
        mock_chroma = mocker.patch("mcp_project_context_server.tools.search_context.chroma_client")
        mock_get_embedding = mocker.patch("mcp_project_context_server.tools.search_context.get_embedding")

        mock_chroma.get_collection.return_value = mock_collection
        mock_collection.count.return_value = 10
        mock_get_embedding.return_value = [0.1, 0.2]
        mock_collection.query.return_value = {
            "documents": [["Doc 1", "Doc 2"]],
            "metadatas": [[{"file": "file1.md"}, {"file": "file2.md"}]],
        }

        result = await handle(arguments)

        assert len(result) == 1
        text = result[0].text
        assert "[file1.md]" in text
        assert "Doc 1" in text
        assert "[file2.md]" in text
        assert "Doc 2" in text

        mock_collection.query.assert_called_once()
        _, kwargs = mock_collection.query.call_args
        assert kwargs["n_results"] == 2

    @pytest.mark.asyncio
    async def test_search_context_not_indexed(self, tmp_path, mocker):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".context").mkdir()

        arguments = {"project_path": str(project_dir), "query": "test"}

        mock_chroma = mocker.patch("mcp_project_context_server.tools.search_context.chroma_client")
        mock_chroma.get_collection.side_effect = Exception("Not found")

        result = await handle(arguments)
        assert "not found. Run index_project_context first." in result[0].text
