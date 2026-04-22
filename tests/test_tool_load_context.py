import pytest

from mcp_project_context_server.tools.load_context import handle, _MIGRATION_NOTICE


class TestLoadContext:
    def setup_method(self):
        pass

    @pytest.mark.asyncio
    async def test_load_context_no_dir(self):
        arguments = {"project_path": "/nonexistent/path"}
        result = await handle(arguments)
        assert len(result) == 1
        assert "No .context/ directory found" in result[0].text

    @pytest.mark.asyncio
    async def test_load_context_full(self, tmp_path, mocker):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()

        (context_dir / "project.md").write_text("Main project", encoding="utf-8")

        decisions_dir = context_dir / "decisions"
        decisions_dir.mkdir()
        (decisions_dir / "001.md").write_text("Decision 1", encoding="utf-8")

        sessions_dir = context_dir / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "2026-01-01.md").write_text("Old Session", encoding="utf-8")
        (sessions_dir / "2026-01-02.md").write_text("New Session", encoding="utf-8")

        # Suppress the migration check so this test is not affected by ChromaDB state
        mocker.patch(
            "mcp_project_context_server.tools.load_context._needs_reindex",
            return_value=False,
        )

        arguments = {"project_path": str(project_dir)}
        result = await handle(arguments)

        assert len(result) == 1
        text = result[0].text
        assert "## project.md" in text
        assert "Main project" in text
        assert "## Architecture Decisions" in text
        assert "001.md" in text
        assert "Decision 1" in text
        assert "## Last Session (2026-01-02)" in text
        assert "New Session" in text
        assert "Old Session" not in text  # Only the latest session


class TestLoadContextMigrationNotice:
    """Test that migration notices appear when collection version mismatches."""

    @pytest.mark.asyncio
    async def test_migration_notice_shown_when_reindex_needed(self, tmp_path, mocker):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        mocker.patch(
            "mcp_project_context_server.tools.load_context._needs_reindex",
            return_value=True,
        )

        result = await handle({"project_path": str(project_dir)})
        text = result[0].text
        assert _MIGRATION_NOTICE in text

    @pytest.mark.asyncio
    async def test_no_migration_notice_when_versions_match(self, tmp_path, mocker):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        mocker.patch(
            "mcp_project_context_server.tools.load_context._needs_reindex",
            return_value=False,
        )

        result = await handle({"project_path": str(project_dir)})
        text = result[0].text
        assert _MIGRATION_NOTICE not in text

    @pytest.mark.asyncio
    async def test_no_migration_notice_when_collection_absent(self, tmp_path, mocker):
        """When the collection doesn't exist yet, _needs_reindex returns False."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        mocker.patch(
            "mcp_project_context_server.tools.load_context._needs_reindex",
            return_value=False,
        )

        result = await handle({"project_path": str(project_dir)})
        text = result[0].text
        assert _MIGRATION_NOTICE not in text

    def test_needs_reindex_returns_false_when_collection_missing(self, mocker):
        """_needs_reindex should gracefully return False when get_collection raises."""
        from mcp_project_context_server.tools.load_context import _needs_reindex
        from pathlib import Path

        mock_context_dir = mocker.MagicMock(spec=Path)
        mocker.patch(
            "mcp_project_context_server.tools.load_context.collection_name_for",
            return_value="test_collection",
        )
        mocker.patch(
            "mcp_project_context_server.tools.load_context.chroma_client.get_collection",
            side_effect=Exception("Collection not found"),
        )

        result = _needs_reindex(mock_context_dir)
        assert result is False

    def test_needs_reindex_returns_true_when_version_missing(self, mocker):
        """A collection with no server_version field should trigger re-index."""
        from mcp_project_context_server.tools.load_context import _needs_reindex
        from pathlib import Path

        mock_collection = mocker.MagicMock()
        mock_collection.metadata = {}  # No server_version key

        mocker.patch(
            "mcp_project_context_server.tools.load_context.collection_name_for",
            return_value="test_collection",
        )
        mocker.patch(
            "mcp_project_context_server.tools.load_context.chroma_client.get_collection",
            return_value=mock_collection,
        )

        result = _needs_reindex(mocker.MagicMock(spec=Path))
        assert result is True

    def test_needs_reindex_returns_false_when_versions_match(self, mocker):
        """Matching server_version means no re-index needed."""
        from mcp_project_context_server.tools import load_context
        from pathlib import Path

        mock_collection = mocker.MagicMock()
        mock_collection.metadata = {"server_version": load_context._SERVER_VERSION}

        mocker.patch(
            "mcp_project_context_server.tools.load_context.collection_name_for",
            return_value="test_collection",
        )
        mocker.patch(
            "mcp_project_context_server.tools.load_context.chroma_client.get_collection",
            return_value=mock_collection,
        )

        result = load_context._needs_reindex(mocker.MagicMock(spec=Path))
        assert result is False

