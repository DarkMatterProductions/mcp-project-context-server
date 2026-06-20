"""Ollama client — DEPRECATED.

This module has been superseded by ``integrations.embeddings``.
Calling any function here will raise a ``RuntimeError``.
"""

_DEPRECATION_MSG = (
    "integrations.ollama is deprecated and no longer supported.\n"
    "Use integrations.embeddings.registry.get_embedding_provider() instead.\n"
    "Set the EMBED_PROVIDER environment variable to 'ollama'."
)


def get_client():  # type: ignore[return]
    raise RuntimeError(_DEPRECATION_MSG)


def get_async_client():  # type: ignore[return]
    raise RuntimeError(_DEPRECATION_MSG)


def get_embedding(text: str) -> list[float]:  # type: ignore[return]
    raise RuntimeError(_DEPRECATION_MSG)


async def get_embedding_async(text: str, client) -> list[float]:  # type: ignore[return]
    raise RuntimeError(_DEPRECATION_MSG)
