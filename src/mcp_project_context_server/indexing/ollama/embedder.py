"""Ollama-specific embedder — DEPRECATED.

This module has been superseded by ``indexing.embedder``, which is provider-agnostic
and selects the embedding backend via the ``EMBED_PROVIDER`` environment variable.
Calling any function here will raise a ``RuntimeError``.
"""

from typing import Any

_DEPRECATION_MSG = (
    "indexing.ollama.embedder is deprecated and no longer supported.\n"
    "Use mcp_project_context_server.indexing.embedder.embed_chunk() instead.\n"
    "Set the EMBED_PROVIDER environment variable to configure the embedding backend."
)


def embed_chunk(text: str) -> list[float]:  # type: ignore[return]
    raise RuntimeError(_DEPRECATION_MSG)


async def embed_chunk_async(text: str, client: Any) -> list[float]:  # type: ignore[return]
    raise RuntimeError(_DEPRECATION_MSG)
