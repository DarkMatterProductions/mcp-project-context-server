"""Loads repo-supplied custom bootstrap questions and merges them with the built-ins."""

import logging
from pathlib import Path

from mcp_project_context_server.helpers.bootstrap_templates import (
    CUSTOM_QUESTIONS_FILENAME,
    PROJECT_QUESTIONS,
    BootstrapQuestion,
    merge_custom_questions,
    parse_custom_questions,
)
from mcp_project_context_server.helpers.context import resolve_project_path
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider

logger = logging.getLogger(__name__)


async def _fetch_custom_questions_file(project_path: str) -> str | None:
    """Return the raw contents of the repo's custom questions file, or None."""
    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(project_path, provider.provider_name)

    if is_remote:
        try:
            return await provider.fetch_root_file(resolved_path, CUSTOM_QUESTIONS_FILENAME)
        except RepositoryError:
            return None

    target = Path(resolved_path) / CUSTOM_QUESTIONS_FILENAME
    if target.is_file():
        return target.read_text(encoding="utf-8")
    return None


async def load_project_questions(project_path: str | None) -> tuple[list[BootstrapQuestion], list[str]]:
    """Return the merged 'project' bootstrap question list plus any warnings.

    If *project_path* is falsy or the repo has no custom questions file, this
    returns the built-in :data:`PROJECT_QUESTIONS` unchanged with no warnings.
    Never raises.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :return: (tuple) A ``(questions, warnings)`` pair.
    """
    if not project_path:
        return list(PROJECT_QUESTIONS), []

    yaml_text = await _fetch_custom_questions_file(project_path)
    if yaml_text is None:
        return list(PROJECT_QUESTIONS), []

    custom_questions, parse_warnings = parse_custom_questions(yaml_text)
    merged, merge_warnings = merge_custom_questions(PROJECT_QUESTIONS, custom_questions)
    return merged, [*parse_warnings, *merge_warnings]
