"""Tests for the create_adr tool."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.create_adr import handle

_EXISTING = """# ADR-00003: Existing Decision

## Status
Accepted

## Context
Existing context.

## ADR Review Discussion
[Discussion pending]

## Decision
[Pending review]

## Consequences
[Pending review]

## Alternatives Considered
[Pending review]
"""


class TestCreateAdrLocal:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_creates_first_adr(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context").mkdir(parents=True)

        result = await handle(
            {"project_path": str(project_dir), "title": "My New Decision", "context": "Because reasons."}
        )

        created = project_dir / ".context" / "decisions" / "ADR-00001-my-new-decision.md"
        assert created.exists()
        content = created.read_text(encoding="utf-8")
        assert "# ADR-00001: My New Decision" in content
        assert "## Status\nProposed" in content
        assert "Because reasons." in content
        assert "[Pending review]" in content
        assert "Created decisions/ADR-00001-my-new-decision.md" in result[0].text
        assert "Run `index_project_context`" in result[0].text

    @pytest.mark.asyncio
    async def test_allocates_next_number_after_existing(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "ADR-00003-existing.md").write_text(_EXISTING, encoding="utf-8")

        await handle({"project_path": str(project_dir), "title": "Next One", "context": "ctx"})

        assert (decisions_dir / "ADR-00004-next-one.md").exists()

    @pytest.mark.asyncio
    async def test_title_kebab_cased(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context").mkdir(parents=True)

        await handle({"project_path": str(project_dir), "title": "Weird Title! With Punctuation?", "context": "ctx"})

        assert (project_dir / ".context" / "decisions" / "ADR-00001-weird-title-with-punctuation.md").exists()

    @pytest.mark.asyncio
    async def test_auto_reindex_runs_indexer(self, tmp_path, mocker):
        project_dir = tmp_path / "project"
        (project_dir / ".context").mkdir(parents=True)
        fake_index_result = [mocker.MagicMock(text="Indexed 1 file.")]
        mocker.patch(
            "mcp_project_context_server.tools.index_context.handle",
            new=AsyncMock(return_value=fake_index_result),
        )

        result = await handle(
            {
                "project_path": str(project_dir),
                "title": "Auto Indexed",
                "context": "ctx",
                "auto_reindex": True,
            }
        )

        assert "Indexed 1 file." in result[0].text

    @pytest.mark.asyncio
    async def test_no_context_dir(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        result = await handle({"project_path": str(project_dir), "title": "X", "context": "ctx"})

        assert "No .context/ directory found" in result[0].text

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo", "title": "X", "context": "ctx"})

        assert "not permitted" in result[0].text


class TestCreateAdrRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_branch_mode_creates_new_adr(self, monkeypatch):
        monkeypatch.delenv("REPO_ADR_WRITE_MODE", raising=False)
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={})

        with (
            patch(
                "mcp_project_context_server.helpers.context_files.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.create_adr.get_repository_provider",
                return_value=mock_provider,
            ),
        ):
            result = await handle({"project_path": "owner/repo", "title": "Remote Decision", "context": "ctx"})

        mock_provider.create_branch.assert_called_once()
        mock_provider.write_file.assert_called_once()
        args, kwargs = mock_provider.write_file.call_args
        assert args[1] == ".context/decisions/ADR-00001-remote-decision.md"
        assert "Remote Decision" in args[2]
        assert "Wrote" in result[0].text
