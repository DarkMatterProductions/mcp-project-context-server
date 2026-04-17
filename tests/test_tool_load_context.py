import pytest
import os
from pathlib import Path
from mcp_project_context_server.tools.load_context import handle

@pytest.mark.asyncio
async def test_load_context_no_dir():
    arguments = {"project_path": "/nonexistent/path"}
    result = await handle(arguments)
    assert len(result) == 1
    assert "No .context/ directory found" in result[0].text

@pytest.mark.asyncio
async def test_load_context_full(tmp_path):
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
    assert "Old Session" not in text # Only the latest session
