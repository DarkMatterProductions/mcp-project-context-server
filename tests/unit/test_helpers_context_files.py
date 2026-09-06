"""Tests for the helpers.context_files module."""

import pytest

from mcp_project_context_server.helpers.context_files import (
    format_tagged_file,
    hash_content,
    list_context_files,
    resolve_requested_files,
)
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing as reset_repo


@pytest.fixture(autouse=True)
def reset_registries():
    reset_repo()
    yield
    reset_repo()


class TestHashContent:
    def test_known_sha512(self):
        assert hash_content("") == (
            "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        )

    def test_different_content_different_hash(self):
        assert hash_content("a") != hash_content("b")

    def test_same_content_same_hash(self):
        assert hash_content("hello world") == hash_content("hello world")


class TestFormatTaggedFile:
    def test_wraps_content_with_path_and_hash(self):
        result = format_tagged_file("project.md", "abc123", "# Title\nBody")
        assert result == '<context-file path="project.md" sha512="abc123">\n# Title\nBody\n</context-file>'


class TestResolveRequestedFilesLocal:
    @pytest.mark.asyncio
    async def test_finds_existing_file(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        found, missing = await resolve_requested_files(str(tmp_path), ["project.md"])

        assert found == {"project.md": "# Project"}
        assert missing == []

    @pytest.mark.asyncio
    async def test_reports_missing_file(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()

        found, missing = await resolve_requested_files(str(tmp_path), ["nope.md"])

        assert found == {}
        assert missing == ["nope.md"]

    @pytest.mark.asyncio
    async def test_no_context_dir_reports_all_missing(self, tmp_path):
        found, missing = await resolve_requested_files(str(tmp_path), ["project.md"])

        assert found == {}
        assert missing == ["project.md"]

    @pytest.mark.asyncio
    async def test_finds_nested_file(self, tmp_path):
        context_dir = tmp_path / ".context"
        (context_dir / "decisions").mkdir(parents=True)
        (context_dir / "decisions" / "0001-foo.md").write_text("# ADR", encoding="utf-8")

        found, missing = await resolve_requested_files(str(tmp_path), ["decisions/0001-foo.md"])

        assert found == {"decisions/0001-foo.md": "# ADR"}
        assert missing == []

    @pytest.mark.asyncio
    async def test_rejects_absolute_path(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        (context_dir / "project.md").write_text("# Project", encoding="utf-8")

        found, missing = await resolve_requested_files(str(tmp_path), [str(context_dir / "project.md")])

        assert found == {}
        assert missing == [str(context_dir / "project.md")]

    @pytest.mark.asyncio
    async def test_rejects_path_traversal(self, tmp_path):
        context_dir = tmp_path / ".context"
        context_dir.mkdir()
        outside = tmp_path / "secret.txt"
        outside.write_text("do not read me", encoding="utf-8")

        found, missing = await resolve_requested_files(str(tmp_path), ["../secret.txt"])

        assert found == {}
        assert missing == ["../secret.txt"]


class TestResolveRequestedFilesRemote:
    @pytest.mark.asyncio
    async def test_finds_requested_files_only(self, mocker):
        provider = mocker.AsyncMock()
        provider.fetch_context_files.return_value = {
            "project.md": "# Project",
            "decisions/0001-foo.md": "# ADR",
        }
        mocker.patch(
            "mcp_project_context_server.helpers.context_files.get_repository_provider",
            return_value=provider,
        )

        found, missing = await resolve_requested_files("owner/repo", ["project.md", "missing.md"])

        assert found == {"project.md": "# Project"}
        assert missing == ["missing.md"]

    @pytest.mark.asyncio
    async def test_repository_error_reports_all_missing(self, mocker):
        provider = mocker.AsyncMock()
        provider.fetch_context_files.side_effect = RepositoryError("boom")
        mocker.patch(
            "mcp_project_context_server.helpers.context_files.get_repository_provider",
            return_value=provider,
        )

        found, missing = await resolve_requested_files("owner/repo", ["project.md"])

        assert found == {}
        assert missing == ["project.md"]


class TestListContextFilesLocal:
    @pytest.mark.asyncio
    async def test_lists_sorted_matching_prefix(self, tmp_path):
        sessions_dir = tmp_path / ".context" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "2026-01-02.md").write_text("b", encoding="utf-8")
        (sessions_dir / "2026-01-01.md").write_text("a", encoding="utf-8")
        (tmp_path / ".context" / "project.md").write_text("# Project", encoding="utf-8")

        result = await list_context_files(str(tmp_path), prefix="sessions/")

        assert result == ["sessions/2026-01-01.md", "sessions/2026-01-02.md"]

    @pytest.mark.asyncio
    async def test_no_context_dir_returns_empty(self, tmp_path):
        result = await list_context_files(str(tmp_path), prefix="sessions/")
        assert result == []

    @pytest.mark.asyncio
    async def test_no_matches_returns_empty(self, tmp_path):
        (tmp_path / ".context").mkdir()
        (tmp_path / ".context" / "project.md").write_text("# Project", encoding="utf-8")

        result = await list_context_files(str(tmp_path), prefix="sessions/")
        assert result == []


class TestListContextFilesRemote:
    @pytest.mark.asyncio
    async def test_lists_sorted_matching_prefix(self, mocker):
        provider = mocker.AsyncMock()
        provider.fetch_context_files.return_value = {
            "sessions/2026-01-02.md": "b",
            "sessions/2026-01-01.md": "a",
            "project.md": "# Project",
        }
        mocker.patch(
            "mcp_project_context_server.helpers.context_files.get_repository_provider",
            return_value=provider,
        )

        result = await list_context_files("owner/repo", prefix="sessions/")

        assert result == ["sessions/2026-01-01.md", "sessions/2026-01-02.md"]

    @pytest.mark.asyncio
    async def test_repository_error_returns_empty(self, mocker):
        provider = mocker.AsyncMock()
        provider.fetch_context_files.side_effect = RepositoryError("boom")
        mocker.patch(
            "mcp_project_context_server.helpers.context_files.get_repository_provider",
            return_value=provider,
        )

        result = await list_context_files("owner/repo", prefix="sessions/")
        assert result == []
