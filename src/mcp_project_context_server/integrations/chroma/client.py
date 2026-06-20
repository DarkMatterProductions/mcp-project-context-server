"""ChromaDB client — DEPRECATED.

This module has been superseded by ``integrations.vectorstore``.
Calling any function or accessing ``chroma_client`` will raise a ``RuntimeError``.
"""

_DEPRECATION_MSG = (
    "integrations.chroma is deprecated and no longer supported.\n"
    "Use integrations.vectorstore.registry.get_vector_store_provider() instead.\n"
    "Set the VECTOR_STORE_PROVIDER environment variable to 'chroma-local' or 'chroma-http'."
)


def get_chroma_client():  # type: ignore[return]
    raise RuntimeError(_DEPRECATION_MSG)


class _LazyChromaClient:
    def __getattr__(self, name: str):  # type: ignore[override]
        raise RuntimeError(_DEPRECATION_MSG)


chroma_client = _LazyChromaClient()
