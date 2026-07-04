"""Integration tests — `index_project_context` tool.

The "no .context/ directory" error path is exercised without any external
services.  All remaining tests require a running ChromaDB instance and an
embedding provider and are marked `pytest.mark.external_services`.

External-service tests are parametrized over every embedding provider
compatible with the default (chroma-local) vector store.  `vertexai` is
excluded — it deadlocks in-process with chromadb on Windows (see
`INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE` in
`integrations/vectorstore/registry.py`) — and is covered separately by
`TestIncompatibleProviders` below, which asserts the clear error instead of a
hang.

A provider is skipped when its opt-out environment variable is set to a
non-empty value:

    SKIP_EMBED_PROVIDER_OLLAMA=1
    SKIP_EMBED_PROVIDER_VOYAGE=1
    SKIP_EMBED_PROVIDER_OPENAI=1
    SKIP_EMBED_PROVIDER_COHERE=1
    SKIP_EMBED_PROVIDER_GOOGLE=1

If the variable is *not* set the test runs — and fails if the provider is
unreachable or not configured.

Run only tests that require no external services:
    pytest tests/integration/test_index_context.py -v -m "not external_services"
"""
import os

import pytest

from tests.integration.base import MCPIntegrationBase
from shared.constructs import CHROMA_COMPATIBLE_PROVIDERS

pytestmark = pytest.mark.asyncio

_TOOL = "index_project_context"


def _provider_param(provider_name: str) -> pytest.param:
    """Return a pytest.param for *provider_name*, marked skip when opted out."""
    env_key = f"SKIP_EMBED_PROVIDER_{provider_name.upper().replace('-', '_')}"
    if os.getenv(env_key):
        return pytest.param(provider_name, marks=pytest.mark.skip(reason=f"{env_key} is set"))
    return pytest.param(provider_name)


class TestIndexContextErrors(MCPIntegrationBase):
    """Error-path tests that require no external services."""

    async def test_missing_context_dir_returns_error_text(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "no_context_here"
        project_dir.mkdir()

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "No .context/ directory found" in text

    async def test_response_is_single_text_content_block_on_error(self, make_mcp_session, tmp_path):
        project_dir = tmp_path / "no_context"
        project_dir.mkdir()

        async with make_mcp_session() as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        assert len(result.content) == 1
        assert result.content[0].type == "text"


class TestIncompatibleProviders(MCPIntegrationBase):
    """Providers known to be incompatible with the default vector store.

    No external services or credentials are needed: the compatibility check
    runs before any provider is constructed, so this returns quickly instead
    of hanging.
    """

    async def test_vertexai_with_chroma_local_returns_clear_error(self, make_mcp_session, tmp_path):
        project_dir = self.make_project(tmp_path, project_md="# Indexed Project\n\nSome content here.")

        async with make_mcp_session({"EMBED_PROVIDER": "vertexai"}) as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        assert result.isError
        text = self.get_tool_text(result)
        assert "cannot be used with" in text
        assert "vertexai" in text
        assert "chroma-local" in text


@pytest.mark.external_services
@pytest.mark.parametrize("embed_provider", [_provider_param(p) for p in CHROMA_COMPATIBLE_PROVIDERS])
class TestIndexContextWithExternalServices(MCPIntegrationBase):
    """Tests that require a running ChromaDB and an embedding provider.

    Parametrized over all supported providers.  Set
    `SKIP_EMBED_PROVIDER_<NAME>=1` to skip a specific provider.
    Skip all with: pytest -m "not external_services"
    """

    async def test_empty_context_dir_indexes_zero_chunks(self, make_mcp_session, tmp_path, embed_provider):
        project_dir = self.make_project(tmp_path)

        async with make_mcp_session({"EMBED_PROVIDER": embed_provider}) as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "Indexed 0 chunks" in text

    async def test_project_md_is_indexed_and_summary_returned(self, make_mcp_session, tmp_path, embed_provider):
        project_dir = self.make_project(tmp_path, project_md="# Indexed Project\n\nSome content here.")

        async with make_mcp_session({"EMBED_PROVIDER": embed_provider}) as session:
            result = await session.call_tool(_TOOL, {"project_path": str(project_dir)})

        text = self.assert_tool_not_error(result)
        assert "Indexed" in text
        assert "chunks" in text

    async def test_index_then_search_returns_results(self, make_mcp_session, tmp_path, embed_provider):
        project_dir = self.make_project(
            tmp_path,
            project_md="# Chromadb Decision\n\nWe chose ChromaDB because it is embeddable.",
        )

        async with make_mcp_session({"EMBED_PROVIDER": embed_provider}) as session:
            await session.call_tool(_TOOL, {"project_path": str(project_dir)})
            search_result = await session.call_tool(
                "search_project_context",
                {"project_path": str(project_dir), "query": "ChromaDB vector store", "n_results": 1},
            )

        text = self.assert_tool_not_error(search_result)
        assert "ChromaDB" in text
