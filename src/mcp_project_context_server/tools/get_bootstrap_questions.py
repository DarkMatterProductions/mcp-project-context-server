"""Tool: get_bootstrap_questions — the interview question set for a bootstrap artifact."""

import logging

from mcp import types

from mcp_project_context_server.helpers.bootstrap_templates import BOOTSTRAP_TARGETS, get_questions
from mcp_project_context_server.helpers.custom_bootstrap_questions import load_project_questions

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``get_bootstrap_questions`` tool call.

    :param arguments: (dict) Tool input dict. Optional key ``"target"``
        (str, default ``"project"``) naming a bootstrap artifact registered in
        :data:`~mcp_project_context_server.helpers.bootstrap_templates.BOOTSTRAP_TARGETS`.
        Optional ``"project_path"`` (str) — when given for the ``"project"``
        target, merges in any repo-supplied custom questions from
        ``.project-bootstrap-questions.yaml`` at the repository root.
    :return: (list) A single :class:`~mcp.types.TextContent` item containing a
        markdown list of interview questions (key, question, help text), or an
        error listing known targets if *target* is unrecognized.
    """
    target = arguments.get("target", "project")
    project_path = arguments.get("project_path")
    warnings: list[str] = []

    if target == "project":
        questions, warnings = await load_project_questions(project_path)
    else:
        questions = get_questions(target)

    if questions is None:
        known = ", ".join(sorted(BOOTSTRAP_TARGETS)) or "none"
        return [types.TextContent(type="text", text=f"Unknown bootstrap target '{target}'. Known targets: {known}.")]

    lines = [f"Interview questions for bootstrapping '{target}':", ""]
    for question in questions:
        lines.append(f"- **{question.key}**: {question.question}")
        lines.append(f"  _{question.help_text}_")
    text = "\n".join(lines)

    if warnings:
        text += "\n\n**Warnings:**\n" + "\n".join(f"- {w}" for w in warnings)

    return [types.TextContent(type="text", text=text)]
