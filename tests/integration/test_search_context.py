"""Integration tests — `search_project_context` tool.

Tests that do NOT require external services (ChromaDB, Ollama) are included
here unconditionally.  Tests that require a running ChromaDB / embedding model
are marked with `pytest.mark.external_services` and are skipped by default
when running with `-m "not external_services"`.

External-service tests are parametrized over every supported embedding
provider.  A provider is skipped when its opt-out environment variable is set
to a non-empty value:

    SKIP_EMBED_PROVIDER_OLLAMA=1
    SKIP_EMBED_PROVIDER_VOYAGE=1
    SKIP_EMBED_PROVIDER_OPENAI=1
    SKIP_EMBED_PROVIDER_COHERE=1
    SKIP_EMBED_PROVIDER_GOOGLE=1
    SKIP_EMBED_PROVIDER_GOOGLE_VERTEX=1

If the variable is *not* set the test runs — and fails if the provider is
unreachable or not configured.

Run the full suite (including external-service tests) with:
    pytest tests/integration/test_search_context.py -v

Run only tests that require no external services:
    pytest tests/integration/test_search_context.py -v -m "not external_services"
"""
import os

import pytest

from tests.integration.base import MCPIntegrationBase
from shared import EMBEDDING_PROVIDER

pytestmark = pytest.mark.asyncio

_TOOL = "search_project_context"


def _provider_param(provider_name: str) -> pytest.param:
    """Return a pytest.param for *provider_name*, marked skip when opted out."""
    env_key = f"SKIP_EMBED_PROVIDER_{provider_name.upper().replace('-', '_')}"
    if os.getenv(env_key):
        return pytest.param(provider_name, marks=pytest.mark.skip(reason=f"{env_key} is set"))
    return pytest.param(provider_name)


class TestSearchContextErrors(MCPIntegrationBase):
    """Error-path tests that require no external services."""

    async def test_missing_context_dir_returns_error_text(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "no_context_here"
        project_dir.mkdir()

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "query": "architecture decisions"},
            )

        text = self.assert_tool_not_error(result)
        assert "No .context/ directory found" in text

    async def test_response_is_single_text_content_block_on_error(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "no_context"
        project_dir.mkdir()

        async with make_mcp_session() as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "query": "anything"},
            )

        assert len(result.content) == 1
        assert result.content[0].type == "text"


@pytest.mark.external_services
@pytest.mark.parametrize("embed_provider", [_provider_param(p) for p in EMBEDDING_PROVIDER])
class TestSearchContextWithVectorStore(MCPIntegrationBase):
    """Tests that require a running ChromaDB and an embedding provider.

    Parametrized over all supported providers.  Set
    `SKIP_EMBED_PROVIDER_<NAME>=1` to skip a specific provider.
    Skip all with: pytest -m "not external_services"
    """

    async def test_unindexed_collection_returns_run_index_message(self, make_mcp_session, tmp_path, embed_provider):
        project_dir = self.make_project(tmp_path, project_md="# A project that has not been indexed")

        async with make_mcp_session({"EMBED_PROVIDER": embed_provider}) as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "query": "architecture"},
            )

        text = self.assert_tool_not_error(result)
        assert "not found" in text.lower() or "index_project_context" in text

    async def test_n_results_parameter_accepted(self, make_mcp_session, tmp_path, embed_provider):
        project_dir = tmp_path / "no_context_for_n_results"
        project_dir.mkdir()

        async with make_mcp_session({"EMBED_PROVIDER": embed_provider}) as session:
            result = await session.call_tool(
                _TOOL,
                {"project_path": str(project_dir), "query": "anything", "n_results": 3},
            )

        assert len(result.content) >= 1
        assert result.content[0].type == "text"
