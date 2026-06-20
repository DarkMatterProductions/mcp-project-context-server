"""Shared fixtures for MCP server integration tests.

These fixtures spin up the real server as a subprocess over stdio, perform the
MCP handshake, and yield a fully-initialised :class:`~mcp.ClientSession`.

Tip: run only integration tests with:
    pytest tests/integration/ -v

Skip tests that need external services (ChromaDB, Ollama) with:
    pytest tests/integration/ -v -m "not external_services"
"""
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_SRC_DIR = str(Path(__file__).parent.parent.parent / "src")


def _build_server_params(extra_env: dict[str, str] | None = None) -> StdioServerParameters:
    """Return ``StdioServerParameters`` for the project-context-server module.

    Strips variables that would silently override tool arguments unless the
    caller explicitly supplies them via *extra_env*.  Always injects the
    project ``src/`` directory into ``PYTHONPATH`` so the subprocess uses the
    current source tree rather than any previously installed wheel.
    """
    env = {**os.environ}
    env.pop("PROJECT_PATH", None)
    env["MCP_TRANSPORT"] = "stdio"
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{_SRC_DIR}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else _SRC_DIR
    if extra_env:
        env.update(extra_env)
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_project_context_server"],
        env=env,
    )


@pytest.fixture
def make_mcp_session():
    """Factory fixture for sessions with custom environment variables.

    Opens a fresh server subprocess per call so tests are fully isolated.
    The async context manager is entered and exited within the test's own
    coroutine, avoiding anyio cancel-scope cross-task issues.

    Usage::

        async def test_something(self, make_mcp_session, tmp_path):
            async with make_mcp_session({"PROJECT_PATH": str(tmp_path)}) as session:
                result = await session.call_tool("list_repositories", {})
    """

    @asynccontextmanager
    async def _factory(extra_env: dict[str, str] | None = None):
        params = _build_server_params(extra_env)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    return _factory
