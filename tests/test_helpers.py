import pytest
from pathlib import Path
from mcp_project_context_server.helpers.context import find_context_dir, collection_name_for, read_context_files


class TestFindContextDir:
    def setup_method(self):
        pass

    def test_finds_context_dir_in_current_directory(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()

        assert find_context_dir(project_dir) == context_dir

    def test_finds_context_dir_in_parent_directory(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()
        subdir = project_dir / "subdir"
        subdir.mkdir()

        assert find_context_dir(subdir) == context_dir

    def test_returns_none_when_context_dir_not_found(self, tmp_path):
        other_dir = tmp_path / "other"
        other_dir.mkdir()

        assert find_context_dir(other_dir) is None


class TestCollectionNameFor:
    def setup_method(self):
        pass

    def test_generates_collection_name(self):
        context_dir = Path("/some/path/my-project/.context")
        assert collection_name_for(context_dir) == "ctx_my_project"

    def test_generates_collection_name_with_spaces(self):
        context_dir_with_spaces = Path("/some/path/My Project/.context")
        assert collection_name_for(context_dir_with_spaces) == "ctx_My_Project"


class TestReadContextFiles:
    def setup_method(self):
        pass

    def test_reads_files_recursively(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()

        (context_dir / "project.md").write_text("Project content", encoding="utf-8")

        decisions_dir = context_dir / "decisions"
        decisions_dir.mkdir()
        (decisions_dir / "adr-001.md").write_text("ADR 1 content", encoding="utf-8")

        files = read_context_files(context_dir)

        assert "project.md" in files
        assert files["project.md"] == "Project content"
        assert "decisions/adr-001.md" in files
        assert files["decisions/adr-001.md"] == "ADR 1 content"
