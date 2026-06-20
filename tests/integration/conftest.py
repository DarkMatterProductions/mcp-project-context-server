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

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _build_server_params(extra_env: dict[str, str] | None = None) -> StdioServerParameters:
    """Return ``StdioServerParameters`` for the project-context-server module.

    Strips variables that would silently override tool arguments unless the
    caller explicitly supplies them via *extra_env*.
    """
    env = {**os.environ}
    env.pop("PROJECT_PATH", None)
    env["MCP_TRANSPORT"] = "stdio"
    if extra_env:
        env.update(extra_env)
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_project_context_server"],
        env=env,
    )


@pytest.fixture
def server_params() -> StdioServerParameters:
    """Default server parameters with no extra environment overrides."""
    return _build_server_params()


@pytest.fixture
async def mcp_session(server_params: StdioServerParameters):
    """A connected, initialised MCP session (function-scoped).

    Spawns a fresh server subprocess per test so tests are fully isolated.
    """
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


@pytest.fixture
def make_mcp_session():
    """Factory fixture for sessions with custom environment variables.

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
