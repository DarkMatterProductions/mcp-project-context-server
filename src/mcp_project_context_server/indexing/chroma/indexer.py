"""Chroma-specific indexer — DEPRECATED.

This module has been superseded by per-provider indexers owned by each vector
store integration:

- ``integrations/vectorstore/chroma_local/indexer.py``  (VECTOR_STORE_PROVIDER=chroma-local)
- ``integrations/vectorstore/chroma_http/indexer.py``   (VECTOR_STORE_PROVIDER=chroma-http)

The shared pipeline logic lives in ``indexing/indexer.py``.
The correct entry point is ``integrations/vectorstore/registry.get_indexer()``,
which returns the right ``index_project_context`` callable for the configured
provider.

Calling ``index_project_context`` here will raise a ``RuntimeError``.
"""

from pathlib import Path

_DEPRECATION_MSG = (
    "indexing.chroma.indexer is deprecated and no longer supported.\n"
    "Use the provider-owned indexer via:\n"
    "  from mcp_project_context_server.integrations.vectorstore.registry import get_indexer\n"
    "  index_project_context = get_indexer()\n"
    "Or import directly from the provider package:\n"
    "  from mcp_project_context_server.integrations.vectorstore.chroma_local.indexer import index_project_context\n"
    "  from mcp_project_context_server.integrations.vectorstore.chroma_http.indexer import index_project_context\n"
    "Set VECTOR_STORE_PROVIDER to select the active provider."
)


async def index_project_context(project_path: str | Path) -> str:  # type: ignore[return]
    raise RuntimeError(_DEPRECATION_MSG)
