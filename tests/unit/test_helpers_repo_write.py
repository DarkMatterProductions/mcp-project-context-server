"""Tests for helpers/repo_write.py — remote write-mode plumbing and reindex notes."""

import pytest

from mcp_project_context_server.helpers.repo_write import append_reindex_note, write_context_file
from mcp_project_context_server.integrations.repository.base import RepositoryError


class _FakeProvider:
    provider_name = "github"

    def __init__(self):
        self.written = []
        self.created_branches = []
        self.default_branch = "main"

    async def write_file(self, repo_id, path, content, commit_message, branch=None):
        self.written.append((repo_id, path, content, commit_message, branch))

    async def create_branch(self, repo_id, branch_name):
        self.created_branches.append((repo_id, branch_name))

    async def get_default_branch(self, repo_id):
        return self.default_branch


class _FailingProvider(_FakeProvider):
    async def write_file(self, repo_id, path, content, commit_message, branch=None):
        raise RepositoryError("write failed")

    async def create_branch(self, repo_id, branch_name):
        raise RepositoryError("branch creation failed")


class TestWriteContextFile:
    @pytest.mark.asyncio
    async def test_branch_mode_default_creates_new_branch(self, monkeypatch):
        monkeypatch.delenv("REPO_ADR_WRITE_MODE", raising=False)
        provider = _FakeProvider()

        message = await write_context_file(provider, "owner/repo", "project.md", "content", "commit msg")

        assert len(provider.created_branches) == 1
        repo_id, branch_name = provider.created_branches[0]
        assert repo_id == "owner/repo"
        assert branch_name.startswith("mcp-adr/")
        assert len(provider.written) == 1
        written_repo_id, path, content, commit_message, branch = provider.written[0]
        assert path == ".context/project.md"
        assert content == "content"
        assert commit_message == "commit msg"
        assert branch == branch_name
        assert branch_name in message
        assert "owner/repo" in message

    @pytest.mark.asyncio
    async def test_direct_mode_writes_to_default_branch(self, monkeypatch):
        monkeypatch.setenv("REPO_ADR_WRITE_MODE", "direct")
        monkeypatch.delenv("REPO_ADR_BRANCH", raising=False)
        provider = _FakeProvider()

        message = await write_context_file(provider, "owner/repo", "decisions/ADR-00001-x.md", "content", "commit")

        assert provider.created_branches == []
        assert len(provider.written) == 1
        _, path, _, _, branch = provider.written[0]
        assert path == ".context/decisions/ADR-00001-x.md"
        assert branch is None
        assert "main" in message

    @pytest.mark.asyncio
    async def test_direct_mode_uses_configured_branch(self, monkeypatch):
        monkeypatch.setenv("REPO_ADR_WRITE_MODE", "direct")
        monkeypatch.setenv("REPO_ADR_BRANCH", "custom-branch")
        provider = _FakeProvider()

        message = await write_context_file(provider, "owner/repo", "project.md", "content", "commit")

        _, _, _, _, branch = provider.written[0]
        assert branch == "custom-branch"
        assert "custom-branch" in message

    @pytest.mark.asyncio
    async def test_direct_mode_write_error_returns_message(self, monkeypatch):
        monkeypatch.setenv("REPO_ADR_WRITE_MODE", "direct")
        provider = _FailingProvider()

        message = await write_context_file(provider, "owner/repo", "project.md", "content", "commit")

        assert "Error writing" in message
        assert "write failed" in message

    @pytest.mark.asyncio
    async def test_branch_mode_branch_creation_error_returns_message(self, monkeypatch):
        monkeypatch.delenv("REPO_ADR_WRITE_MODE", raising=False)
        provider = _FailingProvider()

        message = await write_context_file(provider, "owner/repo", "project.md", "content", "commit")

        assert "Error writing" in message
        assert "branch creation failed" in message


class TestAppendReindexNote:
    @pytest.mark.asyncio
    async def test_manual_reminder_when_auto_reindex_false(self):
        result = await append_reindex_note("some/project", "Wrote file.", False)
        assert result.startswith("Wrote file.")
        assert "Run `index_project_context`" in result

    @pytest.mark.asyncio
    async def test_runs_reindex_when_auto_reindex_true(self, mocker):
        fake_index_result = [mocker.MagicMock(text="Indexed 3 files.")]
        mocker.patch(
            "mcp_project_context_server.tools.index_context.handle",
            new=mocker.AsyncMock(return_value=fake_index_result),
        )

        result = await append_reindex_note("some/project", "Wrote file.", True)

        assert result.startswith("Wrote file.")
        assert "Indexed 3 files." in result
