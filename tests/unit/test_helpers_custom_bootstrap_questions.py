"""Tests for the custom_bootstrap_questions helper."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.helpers.bootstrap_templates import PROJECT_QUESTIONS, BootstrapQuestion
from mcp_project_context_server.helpers.custom_bootstrap_questions import load_project_questions
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing


class TestLoadProjectQuestionsLocal:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_none_project_path_returns_builtins(self):
        questions, warnings = await load_project_questions(None)

        assert questions == list(PROJECT_QUESTIONS)
        assert warnings == []

    @pytest.mark.asyncio
    async def test_missing_file_returns_builtins(self, tmp_path):
        questions, warnings = await load_project_questions(str(tmp_path))

        assert questions == list(PROJECT_QUESTIONS)
        assert warnings == []

    @pytest.mark.asyncio
    async def test_valid_file_merges_custom_question(self, tmp_path):
        (tmp_path / ".project-bootstrap-questions.yaml").write_text(
            "- key: Deployment Target\n  question: Where is this deployed?\n  help_text: e.g. AWS.\n",
            encoding="utf-8",
        )

        questions, warnings = await load_project_questions(str(tmp_path))

        assert warnings == []
        assert questions == [
            *PROJECT_QUESTIONS,
            BootstrapQuestion(key="Deployment Target", question="Where is this deployed?", help_text="e.g. AWS."),
        ]

    @pytest.mark.asyncio
    async def test_malformed_yaml_returns_builtins_and_warning(self, tmp_path):
        (tmp_path / ".project-bootstrap-questions.yaml").write_text("not: valid: yaml: [", encoding="utf-8")

        questions, warnings = await load_project_questions(str(tmp_path))

        assert questions == list(PROJECT_QUESTIONS)
        assert len(warnings) == 1
        assert "Failed to parse" in warnings[0]

    @pytest.mark.asyncio
    async def test_collision_with_builtin_is_skipped_and_warned(self, tmp_path):
        (tmp_path / ".project-bootstrap-questions.yaml").write_text(
            "- key: One-liner\n  question: Overridden?\n",
            encoding="utf-8",
        )

        questions, warnings = await load_project_questions(str(tmp_path))

        assert questions == list(PROJECT_QUESTIONS)
        assert "'One-liner' collides" in warnings[0]


class TestLoadProjectQuestionsRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_valid_file_merges_custom_question(self):
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_root_file = AsyncMock(
            return_value="- key: Deployment Target\n  question: Where is this deployed?\n  help_text: e.g. AWS.\n"
        )

        with patch(
            "mcp_project_context_server.helpers.custom_bootstrap_questions.get_repository_provider",
            return_value=mock_provider,
        ):
            questions, warnings = await load_project_questions("owner/repo")

        assert warnings == []
        assert questions == [
            *PROJECT_QUESTIONS,
            BootstrapQuestion(key="Deployment Target", question="Where is this deployed?", help_text="e.g. AWS."),
        ]
        mock_provider.fetch_root_file.assert_awaited_once_with("owner/repo", ".project-bootstrap-questions.yaml")

    @pytest.mark.asyncio
    async def test_remote_missing_file_returns_builtins(self):
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_root_file = AsyncMock(return_value=None)

        with patch(
            "mcp_project_context_server.helpers.custom_bootstrap_questions.get_repository_provider",
            return_value=mock_provider,
        ):
            questions, warnings = await load_project_questions("owner/repo")

        assert questions == list(PROJECT_QUESTIONS)
        assert warnings == []

    @pytest.mark.asyncio
    async def test_remote_fetch_error_returns_builtins(self):
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_root_file = AsyncMock(side_effect=RepositoryError("boom"))

        with patch(
            "mcp_project_context_server.helpers.custom_bootstrap_questions.get_repository_provider",
            return_value=mock_provider,
        ):
            questions, warnings = await load_project_questions("owner/repo")

        assert questions == list(PROJECT_QUESTIONS)
        assert warnings == []
