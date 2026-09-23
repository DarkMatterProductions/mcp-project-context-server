"""Tests for the get_bootstrap_questions tool."""

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.get_bootstrap_questions import handle


class TestGetBootstrapQuestions:
    @pytest.mark.asyncio
    async def test_default_target_returns_project_questions(self):
        result = await handle({})

        text = result[0].text
        assert "One-liner" in text
        assert "Tech Stack" in text

    @pytest.mark.asyncio
    async def test_explicit_project_target(self):
        result = await handle({"target": "project"})

        assert "Entry Points" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_target_lists_known_targets(self):
        result = await handle({"target": "nonexistent"})

        text = result[0].text
        assert text == "Unknown bootstrap target 'nonexistent'. Known targets: project."
        assert "project" in text


class TestGetBootstrapQuestionsWithProjectPath:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_custom_questions_merged_into_output(self, tmp_path):
        (tmp_path / ".project-bootstrap-questions.yaml").write_text(
            "- key: Deployment Target\n  question: Where is this deployed?\n  help_text: e.g. AWS.\n",
            encoding="utf-8",
        )

        result = await handle({"target": "project", "project_path": str(tmp_path)})

        text = result[0].text
        assert "**Deployment Target**: Where is this deployed?" in text
        assert "One-liner" in text
        assert "**Warnings:**" not in text

    @pytest.mark.asyncio
    async def test_collision_produces_warning_and_keeps_builtin(self, tmp_path):
        (tmp_path / ".project-bootstrap-questions.yaml").write_text(
            "- key: One-liner\n  question: Overridden question?\n",
            encoding="utf-8",
        )

        result = await handle({"target": "project", "project_path": str(tmp_path)})

        text = result[0].text
        assert "**One-liner**: In one sentence, what does this project do?" in text
        assert "**Warnings:**" in text
        assert "'One-liner' collides" in text

    @pytest.mark.asyncio
    async def test_malformed_yaml_returns_builtins_with_warning(self, tmp_path):
        (tmp_path / ".project-bootstrap-questions.yaml").write_text("not: valid: yaml: [", encoding="utf-8")

        result = await handle({"target": "project", "project_path": str(tmp_path)})

        text = result[0].text
        assert "One-liner" in text
        assert "**Warnings:**" in text
        assert "Failed to parse" in text

    @pytest.mark.asyncio
    async def test_missing_file_reproduces_default_output(self, tmp_path):
        result = await handle({"target": "project", "project_path": str(tmp_path)})

        text = result[0].text
        assert "One-liner" in text
        assert "**Warnings:**" not in text
