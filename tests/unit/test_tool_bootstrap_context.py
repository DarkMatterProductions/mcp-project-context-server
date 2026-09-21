"""Tests for the bootstrap_context tool."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.bootstrap_context import _read_template, handle

_SECTIONS = {
    "One-liner": "Does a thing.",
    "Tech Stack": "Python.",
}


class TestBootstrapContextLocal:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_fresh_project_creates_all_artifacts(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        result = await handle(
            {
                "project_path": str(project_dir),
                "project_name": "My Project",
                "project_sections": _SECTIONS,
            }
        )

        context_dir = project_dir / ".context"
        assert (context_dir / "decisions").is_dir()
        assert (context_dir / "sessions").is_dir()

        governance_doc = (context_dir / "ADR_CREATE_AND_MANAGEMENT.md").read_text(encoding="utf-8")
        assert governance_doc == _read_template("ADR_CREATE_AND_MANAGEMENT.md")

        planning_doc = (context_dir / "PLANNING_LOOP.md").read_text(encoding="utf-8")
        assert planning_doc == _read_template("PLANNING_LOOP.md")

        project_md = (context_dir / "project.md").read_text(encoding="utf-8")
        assert "# Project: My Project" in project_md
        assert "Does a thing." in project_md

        adr_file = (
            context_dir
            / "decisions"
            / "ADR-00001-consistent-use-of-architecture-decision-records-in-the-standard-development-cycle.md"
        )
        assert adr_file.exists()
        assert "Status\nProposed" in adr_file.read_text(encoding="utf-8")

        text = result[0].text
        assert "Bootstrapped .context/ for 'My Project'" in text
        assert "Run `index_project_context`" in text

    @pytest.mark.asyncio
    async def test_rerun_skips_everything(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        arguments = {
            "project_path": str(project_dir),
            "project_name": "My Project",
            "project_sections": _SECTIONS,
        }

        await handle(arguments)
        result = await handle(arguments)

        text = result[0].text
        assert "skipped (already exists)" in text
        assert "skipped (an ADR already exists)" in text

    @pytest.mark.asyncio
    async def test_partial_state_skips_only_existing_project_md(self, tmp_path):
        project_dir = tmp_path / "project"
        context_dir = project_dir / ".context"
        context_dir.mkdir(parents=True)
        (context_dir / "project.md").write_text("Pre-existing content.", encoding="utf-8")

        result = await handle(
            {
                "project_path": str(project_dir),
                "project_name": "My Project",
                "project_sections": _SECTIONS,
            }
        )

        assert (context_dir / "project.md").read_text(encoding="utf-8") == "Pre-existing content."
        assert (context_dir / "ADR_CREATE_AND_MANAGEMENT.md").exists()
        assert (
            context_dir
            / "decisions"
            / "ADR-00001-consistent-use-of-architecture-decision-records-in-the-standard-development-cycle.md"
        ).exists()

        text = result[0].text
        assert "`.context/project.md`: skipped (already exists)." in text

    @pytest.mark.asyncio
    async def test_not_a_directory_returns_error(self, tmp_path):
        missing = tmp_path / "does-not-exist"

        result = await handle({"project_path": str(missing), "project_name": "X"})

        assert "is not an existing directory" in result[0].text

    @pytest.mark.asyncio
    async def test_auto_reindex_runs_indexer(self, tmp_path, mocker):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        fake_index_result = [mocker.MagicMock(text="Indexed 5 files.")]
        mocker.patch(
            "mcp_project_context_server.tools.index_context.handle",
            new=AsyncMock(return_value=fake_index_result),
        )

        result = await handle(
            {
                "project_path": str(project_dir),
                "project_name": "My Project",
                "auto_reindex": True,
            }
        )

        assert "Indexed 5 files." in result[0].text

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle({"project_path": "unapproved-org/some-repo", "project_name": "X"})

        assert "not permitted" in result[0].text

    @pytest.mark.asyncio
    async def test_custom_question_answer_appears_in_project_md(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".project-bootstrap-questions.yaml").write_text(
            "- key: Deployment Target\n  question: Where is this deployed?\n  help_text: e.g. AWS, on-prem.\n",
            encoding="utf-8",
        )

        result = await handle(
            {
                "project_path": str(project_dir),
                "project_name": "My Project",
                "project_sections": {**_SECTIONS, "Deployment Target": "AWS Lambda."},
            }
        )

        project_md = (project_dir / ".context" / "project.md").read_text(encoding="utf-8")
        assert "AWS Lambda." in project_md
        assert "**Warnings:**" not in result[0].text

    @pytest.mark.asyncio
    async def test_custom_question_collision_reports_warning_and_keeps_builtin(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".project-bootstrap-questions.yaml").write_text(
            "- key: One-liner\n  question: Overridden question?\n  help_text: Should be skipped.\n",
            encoding="utf-8",
        )

        result = await handle(
            {
                "project_path": str(project_dir),
                "project_name": "My Project",
                "project_sections": _SECTIONS,
            }
        )

        text = result[0].text
        assert "**Warnings:**" in text
        assert "'One-liner' collides" in text

        project_md = (project_dir / ".context" / "project.md").read_text(encoding="utf-8")
        assert "Does a thing." in project_md

    @pytest.mark.asyncio
    async def test_malformed_custom_questions_yaml_does_not_crash(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".project-bootstrap-questions.yaml").write_text(
            "not: valid: yaml: [",
            encoding="utf-8",
        )

        result = await handle(
            {
                "project_path": str(project_dir),
                "project_name": "My Project",
                "project_sections": _SECTIONS,
            }
        )

        text = result[0].text
        assert "**Warnings:**" in text
        assert "Failed to parse" in text
        assert (project_dir / ".context" / "project.md").exists()


class TestBootstrapContextRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_branch_mode_creates_artifacts(self, monkeypatch):
        monkeypatch.delenv("REPO_ADR_WRITE_MODE", raising=False)
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={})
        mock_provider.fetch_root_file = AsyncMock(return_value=None)

        with (
            patch(
                "mcp_project_context_server.helpers.context_files.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.bootstrap_context.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.create_adr.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.write_project.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.helpers.custom_bootstrap_questions.get_repository_provider",
                return_value=mock_provider,
            ),
        ):
            result = await handle(
                {
                    "project_path": "owner/repo",
                    "project_name": "Remote Project",
                    "project_sections": _SECTIONS,
                }
            )

        assert mock_provider.create_branch.call_count >= 1
        written_paths = [call.args[1] for call in mock_provider.write_file.call_args_list]
        assert ".context/ADR_CREATE_AND_MANAGEMENT.md" in written_paths
        assert ".context/PLANNING_LOOP.md" in written_paths
        assert ".context/project.md" in written_paths
        assert any(p.startswith(".context/decisions/ADR-00001-") for p in written_paths)

        text = result[0].text
        assert "Bootstrapped .context/ for 'Remote Project'" in text

    @pytest.mark.asyncio
    async def test_remote_custom_question_answer_appears_in_project_md(self, monkeypatch):
        monkeypatch.delenv("REPO_ADR_WRITE_MODE", raising=False)
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(return_value={})
        mock_provider.fetch_root_file = AsyncMock(
            return_value="- key: Deployment Target\n  question: Where is this deployed?\n  help_text: e.g. AWS.\n"
        )

        with (
            patch(
                "mcp_project_context_server.helpers.context_files.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.bootstrap_context.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.create_adr.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.write_project.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.helpers.custom_bootstrap_questions.get_repository_provider",
                return_value=mock_provider,
            ),
        ):
            result = await handle(
                {
                    "project_path": "owner/repo",
                    "project_name": "Remote Project",
                    "project_sections": {**_SECTIONS, "Deployment Target": "AWS Lambda."},
                }
            )

        written_files = {call.args[1]: call.args[2] for call in mock_provider.write_file.call_args_list}
        assert "AWS Lambda." in written_files[".context/project.md"]
        assert "**Warnings:**" not in result[0].text
