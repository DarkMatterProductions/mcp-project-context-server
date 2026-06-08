"""Tests for the local filesystem repository provider."""
import os

import pytest
import pytest_asyncio

from mcp_project_context_server.integrations.repository.local.client import LocalRepositoryProvider


@pytest.fixture()
def provider():
    return LocalRepositoryProvider()


class TestFetchContextFiles:
    """Tests for LocalRepositoryProvider.fetch_context_files."""

    @pytest.mark.asyncio
    async def test_returns_empty_dict_when_no_context_dir(self, tmp_path, provider):
        result = await provider.fetch_context_files(str(tmp_path))
        assert result == {}

    @pytest.mark.asyncio
    async def test_returns_md_files_from_context_dir(self, tmp_path, provider):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project")
        sub = context_dir / "adrs"
        sub.mkdir()
        (sub / "001.md").write_text("# ADR 001")

        result = await provider.fetch_context_files(str(tmp_path))

        assert "project.md" in result
        assert result["project.md"] == "# Project"
        assert "adrs/001.md" in result
        assert result["adrs/001.md"] == "# ADR 001"

    @pytest.mark.asyncio
    async def test_ignores_non_md_files(self, tmp_path, provider):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "readme.md").write_text("# Readme")
        (context_dir / "notes.txt").write_text("plain text")

        result = await provider.fetch_context_files(str(tmp_path))

        assert "readme.md" in result
        assert "notes.txt" not in result


class TestFetchSourceBundle:
    """Tests for LocalRepositoryProvider.fetch_source_bundle."""

    @pytest.mark.asyncio
    async def test_returns_none_when_no_bundle(self, tmp_path, provider):
        result = await provider.fetch_source_bundle(str(tmp_path))
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_content_when_bundle_exists(self, tmp_path, provider):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "BUNDLE.md").write_text("# Bundle content")

        result = await provider.fetch_source_bundle(str(tmp_path))

        assert result == "# Bundle content"


class TestWriteFile:
    """Tests for LocalRepositoryProvider.write_file."""

    @pytest.mark.asyncio
    async def test_creates_file_and_parent_dirs(self, tmp_path, provider):
        await provider.write_file(str(tmp_path), "sub/dir/file.py", "print('hi')", "ignored")

        target = tmp_path / "sub" / "dir" / "file.py"
        assert target.is_file()
        assert target.read_text() == "print('hi')"

    @pytest.mark.asyncio
    async def test_message_is_ignored(self, tmp_path, provider):
        # Just ensures no error is raised
        await provider.write_file(str(tmp_path), "hello.py", "x = 1", "commit msg")
        assert (tmp_path / "hello.py").is_file()


class TestListRepositories:
    """Tests for LocalRepositoryProvider.list_repositories."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_project_path_not_set(self, monkeypatch):
        monkeypatch.delenv("PROJECT_PATH", raising=False)
        p = LocalRepositoryProvider()
        result = await p.list_repositories()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_single_entry_when_project_path_set(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PROJECT_PATH", str(tmp_path))
        p = LocalRepositoryProvider()
        result = await p.list_repositories()
        assert len(result) == 1
        assert result[0].identifier == str(tmp_path)
        assert result[0].indexed is False
