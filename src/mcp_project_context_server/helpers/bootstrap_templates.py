"""Question registry and rendering helpers for bootstrapping new .context/ projects."""

from dataclasses import dataclass

import yaml

_ADR_DEFAULT = "See `.context/decisions/`. ADR-00001 establishes this project's ADR process."

CUSTOM_QUESTIONS_FILENAME = ".project-bootstrap-questions.yaml"


@dataclass(frozen=True)
class BootstrapQuestion:
    key: str
    question: str
    help_text: str


PROJECT_QUESTIONS: list[BootstrapQuestion] = [
    BootstrapQuestion(
        key="One-liner",
        question="In one sentence, what does this project do?",
        help_text="A short summary that orients a new contributor immediately.",
    ),
    BootstrapQuestion(
        key="Tech Stack",
        question="What languages, frameworks, and major libraries does this project use?",
        help_text="List the primary technologies, e.g. language, runtime, key frameworks/libraries.",
    ),
    BootstrapQuestion(
        key="Architecture",
        question="How is the project structured at a high level?",
        help_text="Describe major components/modules and how they interact.",
    ),
    BootstrapQuestion(
        key="Key Conventions",
        question="What conventions or standards should contributors follow?",
        help_text="Naming conventions, code style, testing patterns, or other project-specific norms.",
    ),
    BootstrapQuestion(
        key="Current Active Work",
        question="What is currently being worked on?",
        help_text="In-flight features, migrations, or initiatives.",
    ),
    BootstrapQuestion(
        key="Known Pain Points / Tech Debt",
        question="What are the known pain points or areas of technical debt?",
        help_text="Anything that slows development down or is due for cleanup.",
    ),
    BootstrapQuestion(
        key="Entry Points",
        question="What are the main entry points into the codebase?",
        help_text="Files or commands a new contributor would start from, e.g. main module, CLI entry, server startup.",
    ),
]

BOOTSTRAP_TARGETS: dict[str, list[BootstrapQuestion]] = {
    "project": PROJECT_QUESTIONS,
}


def get_questions(target: str) -> list[BootstrapQuestion]:
    return BOOTSTRAP_TARGETS.get(target, [])


def render_project_md(name: str, sections: dict[str, str], questions: list[BootstrapQuestion] | None = None) -> str:
    lines = [f"# Project: {name}", ""]
    for question in questions if questions is not None else PROJECT_QUESTIONS:
        lines.append(f"## {question.key}")
        lines.append(sections.get(question.key, "[TBD]").strip())
        lines.append("")
    lines.append("## ADRs")
    lines.append(sections.get("ADRs", _ADR_DEFAULT).strip())
    lines.append("")
    return "\n".join(lines)


def parse_custom_questions(yaml_text: str) -> tuple[list[BootstrapQuestion], list[str]]:
    """Parse repo-supplied custom bootstrap questions from YAML text.

    Never raises — malformed content is skipped and reported as a warning.

    :param yaml_text: (str) The raw contents of ``.project-bootstrap-questions.yaml``.
    :return: (tuple) A ``(questions, warnings)`` pair.
    """
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return [], [f"Failed to parse '{CUSTOM_QUESTIONS_FILENAME}': {exc}"]

    if data is None:
        return [], []

    if not isinstance(data, list):
        return [], [f"'{CUSTOM_QUESTIONS_FILENAME}' top-level content must be a list of questions."]

    questions: list[BootstrapQuestion] = []
    warnings: list[str] = []
    for index, entry in enumerate(data):
        if not isinstance(entry, dict):
            warnings.append(f"'{CUSTOM_QUESTIONS_FILENAME}' entry {index} is not a mapping and was skipped.")
            continue
        key = entry.get("key")
        question = entry.get("question")
        if not key or not question:
            warnings.append(
                f"'{CUSTOM_QUESTIONS_FILENAME}' entry {index} is missing 'key' or 'question' and was skipped."
            )
            continue
        questions.append(
            BootstrapQuestion(key=str(key), question=str(question), help_text=str(entry.get("help_text", "")))
        )

    return questions, warnings


def merge_custom_questions(
    base: list[BootstrapQuestion], custom: list[BootstrapQuestion]
) -> tuple[list[BootstrapQuestion], list[str]]:
    """Merge *custom* questions after *base*, dropping any that collide by key.

    :param base: (list) The built-in question list. Always wins on key collision.
    :param custom: (list) Repo-supplied custom questions to append.
    :return: (tuple) A ``(merged, warnings)`` pair.
    """
    used_keys = {question.key for question in base}
    merged = list(base)
    warnings: list[str] = []
    for question in custom:
        if question.key in used_keys:
            warnings.append(f"Custom question '{question.key}' collides with an existing question and was skipped.")
            continue
        used_keys.add(question.key)
        merged.append(question)
    return merged, warnings
