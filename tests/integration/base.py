"""Shared base class for all MCP server integration tests.

Every integration test class should inherit from `MCPIntegrationBase` so that
common server-params construction, project scaffolding, and response-assertion
helpers are available without duplication.
"""
import os
import sys
from pathlib import Path

from mcp import StdioServerParameters

from tests.shared import KNOWN_INTERFERING_ENV_VARS, SRC_DIR


class MCPIntegrationBase:
    """Helpers shared across all MCP server integration test classes.

    Tests should use the `mcp_session` and `make_mcp_session` fixtures
    from `conftest.py` for their session lifecycle.  The helpers here exist
    for edge-case tests that need custom server configuration or fine-grained
    project structure control.
    """

    # ------------------------------------------------------------------
    # Server parameters
    # ------------------------------------------------------------------

    @classmethod
    def build_server_params(cls, extra_env: dict[str, str] | None = None) -> StdioServerParameters:
        """Build `StdioServerParameters` pointing at the installed server module.

        Inherits the current process environment but strips variables that would
        silently override tool arguments (e.g. `PROJECT_PATH`) unless the
        caller explicitly supplies them via *extra_env*.

        Args:
            extra_env: Additional environment variables passed to the server
                process.  These take precedence over the inherited environment.

        Returns:
            A :class:`~mcp.StdioServerParameters` instance ready for use with
            :func:`~mcp.client.stdio.stdio_client`.
        """
        env = {**os.environ}
        for var in KNOWN_INTERFERING_ENV_VARS:
            env.pop(var, None)
        env["MCP_TRANSPORT"] = "stdio"
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{SRC_DIR}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else SRC_DIR
        if extra_env:
            env.update(extra_env)
        return StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_project_context_server"],
            env=env,
        )

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_tool_text(result) -> str:
        """Extract the text from the first content item of a `call_tool` result.

        Args:
            result: The `CallToolResult` returned by `session.call_tool()`.

        Returns:
            The `.text` field of the first content block.

        Raises:
            AssertionError: If the content list is empty or the first item is
                not a text block.
        """
        assert result.content, "call_tool result has no content"
        assert result.content[0].type == "text", (
            f"Expected text content, got {result.content[0].type!r}"
        )
        return result.content[0].text

    @staticmethod
    def assert_tool_not_error(result) -> str:
        """Assert the tool call did not error and return its text.

        Args:
            result: The `CallToolResult` returned by `session.call_tool()`.

        Returns:
            The text from the first content block.

        Raises:
            AssertionError: If `result.isError` is `True`.
        """
        assert not getattr(result, "isError", False), (
            f"Tool call unexpectedly errored: {result}"
        )
        return MCPIntegrationBase.get_tool_text(result)

    # ------------------------------------------------------------------
    # Project scaffolding
    # ------------------------------------------------------------------

    @classmethod
    def make_project(
        cls,
        tmp_path: Path,
        *,
        project_md: str | None = None,
        decisions: dict[str, str] | None = None,
        sessions: dict[str, str] | None = None,
    ) -> Path:
        """Create a minimal project tree with a `.context/` directory.

        Args:
            tmp_path: The `pytest` `tmp_path` fixture value.
            project_md: Content to write to `.context/project.md`.  The file
                is omitted when *project_md* is `None`.
            decisions: Mapping of `{filename: content}` for files under
                `.context/decisions/`.  The sub-directory is omitted when
                *decisions* is `None` or empty.
            sessions: Mapping of `{filename: content}` for files under
                `.context/sessions/`.  The sub-directory is omitted when
                *sessions* is `None` or empty.

        Returns:
            The project root :class:`~pathlib.Path` (the parent of `.context/`).
        """
        project_dir = tmp_path / f"project_{tmp_path.name}"
        project_dir.mkdir()
        context_dir = project_dir / ".context"
        context_dir.mkdir()

        if project_md is not None:
            (context_dir / "project.md").write_text(project_md, encoding="utf-8")

        if decisions:
            decisions_dir = context_dir / "decisions"
            decisions_dir.mkdir()
            for name, content in decisions.items():
                (decisions_dir / name).write_text(content, encoding="utf-8")

        if sessions:
            sessions_dir = context_dir / "sessions"
            sessions_dir.mkdir()
            for name, content in sessions.items():
                (sessions_dir / name).write_text(content, encoding="utf-8")

        return project_dir
