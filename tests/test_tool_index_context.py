import pytest

from mcp_project_context_server.tools.index_context import handle


class TestIndexContext:
    def setup_method(self):
        self.arguments = {"project_path": "/some/path"}

    @pytest.mark.asyncio
    async def test_index_context_calls_index_and_returns_result(self, mocker):
        mock_index = mocker.patch(
            "mcp_project_context_server.tools.index_context.index_project_context",
            new_callable=mocker.AsyncMock,
        )
        mock_index.return_value = "Indexed 5 files."

        result = await handle(self.arguments)

        assert len(result) == 1
        assert result[0].text == "Indexed 5 files."
        mock_index.assert_called_once_with("/some/path")


class TestIndexerChunkerIntegration:
    """Verify that the indexer uses chunk_markdown and stores server_version."""

    @pytest.mark.asyncio
    async def test_indexer_uses_chunk_markdown(self, mocker, tmp_path):
        """chunk_markdown should be called for each file during indexing."""
        from mcp_project_context_server.indexing.chroma import indexer

        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("## Status\n\nActive", encoding="utf-8")

        mock_chunk = mocker.patch.object(
            indexer,
            "chunk_markdown",
            wraps=lambda text, size: ["chunk1"],
        )

        # Mock ChromaDB and embedder to avoid real network calls
        mock_collection = mocker.MagicMock()
        mocker.patch.object(indexer.chroma_client, "delete_collection", return_value=None)
        mocker.patch.object(indexer.chroma_client, "create_collection", return_value=mock_collection)
        mocker.patch(
            "mcp_project_context_server.indexing.chroma.indexer.embed_chunk_async",
            new_callable=mocker.AsyncMock,
            return_value=[0.1, 0.2, 0.3],
        )
        mocker.patch(
            "mcp_project_context_server.indexing.chroma.indexer.get_async_client",
            return_value=mocker.MagicMock(),
        )

        result = await indexer.index_project_context(tmp_path)

        assert mock_chunk.called
        assert "Indexed" in result

    @pytest.mark.asyncio
    async def test_collection_created_with_server_version_metadata(self, mocker, tmp_path):
        """create_collection must be called with server_version in metadata."""
        from mcp_project_context_server.indexing.chroma import indexer

        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("## Status\n\nActive", encoding="utf-8")

        mock_collection = mocker.MagicMock()
        mocker.patch.object(indexer.chroma_client, "delete_collection", return_value=None)
        create_spy = mocker.patch.object(
            indexer.chroma_client, "create_collection", return_value=mock_collection
        )
        mocker.patch(
            "mcp_project_context_server.indexing.chroma.indexer.embed_chunk_async",
            new_callable=mocker.AsyncMock,
            return_value=[0.1, 0.2, 0.3],
        )
        mocker.patch(
            "mcp_project_context_server.indexing.chroma.indexer.get_async_client",
            return_value=mocker.MagicMock(),
        )

        await indexer.index_project_context(tmp_path)

        _call_kwargs = create_spy.call_args
        metadata_arg = _call_kwargs.kwargs.get("metadata") or (_call_kwargs.args[1] if len(_call_kwargs.args) > 1 else None)
        assert metadata_arg is not None
        assert "server_version" in metadata_arg

