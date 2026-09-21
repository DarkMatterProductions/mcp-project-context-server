"""Tests for the bootstrap_templates helper."""

from mcp_project_context_server.helpers.bootstrap_templates import (
    BOOTSTRAP_TARGETS,
    PROJECT_QUESTIONS,
    BootstrapQuestion,
    get_questions,
    merge_custom_questions,
    parse_custom_questions,
    render_project_md,
)


class TestGetQuestions:
    def test_known_target_returns_project_questions(self):
        assert get_questions("project") == PROJECT_QUESTIONS

    def test_unknown_target_returns_none(self):
        assert get_questions("nonexistent") is None

    def test_registry_contains_project(self):
        assert "project" in BOOTSTRAP_TARGETS


class TestRenderProjectMd:
    def test_renders_all_answered_sections(self):
        sections = {q.key: f"answer for {q.key}" for q in PROJECT_QUESTIONS}
        sections["ADRs"] = "Custom ADR note."

        content = render_project_md("My Project", sections)

        assert content.startswith("# Project: My Project\n")
        for question in PROJECT_QUESTIONS:
            assert f"## {question.key}" in content
            assert f"answer for {question.key}" in content
        assert "## ADRs" in content
        assert "Custom ADR note." in content

    def test_missing_sections_get_placeholder(self):
        content = render_project_md("Empty Project", {})

        for question in PROJECT_QUESTIONS:
            assert f"## {question.key}\n[TBD]" in content

    def test_missing_adrs_section_gets_default(self):
        content = render_project_md("Empty Project", {})

        assert "ADR-00001 establishes this project's ADR process." in content

    def test_explicit_questions_list_overrides_default(self):
        custom = [BootstrapQuestion(key="Deployment Target", question="Where?", help_text="")]

        content = render_project_md("My Project", {"Deployment Target": "AWS."}, custom)

        assert "## Deployment Target" in content
        assert "AWS." in content
        assert "## One-liner" not in content

    def test_none_questions_falls_back_to_project_questions(self):
        content = render_project_md("My Project", {}, None)

        for question in PROJECT_QUESTIONS:
            assert f"## {question.key}" in content


class TestParseCustomQuestions:
    def test_valid_list(self):
        yaml_text = (
            "- key: Deployment Target\n"
            "  question: Where is this deployed?\n"
            "  help_text: e.g. AWS, on-prem.\n"
            "- key: Team Ownership\n"
            "  question: Who owns this?\n"
        )

        questions, warnings = parse_custom_questions(yaml_text)

        assert warnings == []
        assert questions == [
            BootstrapQuestion(
                key="Deployment Target", question="Where is this deployed?", help_text="e.g. AWS, on-prem."
            ),
            BootstrapQuestion(key="Team Ownership", question="Who owns this?", help_text=""),
        ]

    def test_invalid_yaml_returns_warning(self):
        questions, warnings = parse_custom_questions("not: valid: yaml: [")

        assert questions == []
        assert len(warnings) == 1
        assert "Failed to parse" in warnings[0]

    def test_non_list_top_level_returns_warning(self):
        questions, warnings = parse_custom_questions("key: value\n")

        assert questions == []
        assert "must be a list" in warnings[0]

    def test_empty_file_returns_no_questions_and_no_warnings(self):
        questions, warnings = parse_custom_questions("")

        assert questions == []
        assert warnings == []

    def test_entry_missing_key_or_question_is_skipped(self):
        yaml_text = "- key: Foo\n  help_text: no question here\n- question: no key here\n"

        questions, warnings = parse_custom_questions(yaml_text)

        assert questions == []
        assert len(warnings) == 2
        assert "entry 0" in warnings[0]
        assert "entry 1" in warnings[1]

    def test_non_dict_entry_is_skipped(self):
        questions, warnings = parse_custom_questions("- just a string\n")

        assert questions == []
        assert "entry 0 is not a mapping" in warnings[0]

    def test_missing_help_text_defaults_to_empty_string(self):
        questions, warnings = parse_custom_questions("- key: Foo\n  question: A question?\n")

        assert warnings == []
        assert questions == [BootstrapQuestion(key="Foo", question="A question?", help_text="")]


class TestMergeCustomQuestions:
    def test_no_collision_appends_custom_after_base(self):
        custom = [BootstrapQuestion(key="Deployment Target", question="Where?", help_text="")]

        merged, warnings = merge_custom_questions(PROJECT_QUESTIONS, custom)

        assert warnings == []
        assert merged == [*PROJECT_QUESTIONS, *custom]

    def test_collision_with_builtin_drops_custom_and_warns(self):
        custom = [BootstrapQuestion(key="One-liner", question="Overridden?", help_text="")]

        merged, warnings = merge_custom_questions(PROJECT_QUESTIONS, custom)

        assert merged == list(PROJECT_QUESTIONS)
        assert "'One-liner' collides" in warnings[0]

    def test_collision_between_two_custom_entries_drops_second(self):
        custom = [
            BootstrapQuestion(key="Deployment Target", question="Where first?", help_text=""),
            BootstrapQuestion(key="Deployment Target", question="Where second?", help_text=""),
        ]

        merged, warnings = merge_custom_questions(PROJECT_QUESTIONS, custom)

        assert merged == [*PROJECT_QUESTIONS, custom[0]]
        assert "'Deployment Target' collides" in warnings[0]
