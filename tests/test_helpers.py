import pytest
from pathlib import Path
from mcp_project_context_server.helpers.context import find_context_dir, collection_name_for, read_context_files

def test_find_context_dir(tmp_path):
    # Test case 1: .context in the current directory
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    context_dir = project_dir / ".context"
    context_dir.mkdir()
    
    assert find_context_dir(project_dir) == context_dir
    
    # Test case 2: .context in a parent directory
    subdir = project_dir / "subdir"
    subdir.mkdir()
    assert find_context_dir(subdir) == context_dir
    
    # Test case 3: .context not found
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    assert find_context_dir(other_dir) is None

def test_collection_name_for():
    context_dir = Path("/some/path/my-project/.context")
    assert collection_name_for(context_dir) == "ctx_my_project"
    
    context_dir_with_spaces = Path("/some/path/My Project/.context")
    assert collection_name_for(context_dir_with_spaces) == "ctx_My_Project"

def test_read_context_files(tmp_path):
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
