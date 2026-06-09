"""ChromaDB client configuration and lazy singleton."""

import os
from pathlib import Path
from typing import Optional

import chromadb
import chromadb.api
from chromadb.config import Settings

_chroma_default: Path = Path.home() / ".mcp-data" / "chroma"
CHROMA_DIR: Path = Path(os.getenv("CHROMA_DIR", str(_chroma_default)))

_chroma_instance: Optional[chromadb.api.ClientAPI] = None


def get_chroma_client() -> chromadb.api.ClientAPI:
    """Return the ChromaDB singleton, creating it on first call.

    Initialization is deferred to first use so that importing this module does not
    trigger filesystem side-effects (directory creation, database connection) at
    import time — which interferes with testing and lazy startup patterns.
    """
    global _chroma_instance
    if _chroma_instance is None:
        # chromadb.PersistentClient requires a str — explicit conversion at the
        # external API boundary is the only place this conversion should occur.
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _chroma_instance = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    return _chroma_instance


# Module-level alias for backward compatibility with existing callers.
# Accessing attributes on this object will trigger lazy initialization on first use.
class _LazyChromaClient:
    """Thin proxy that defers ChromaDB initialization to first attribute access."""

    def __getattr__(self, name: str):  # type: ignore[override]
        return getattr(get_chroma_client(), name)


chroma_client: chromadb.api.ClientAPI = _LazyChromaClient()  # type: ignore[assignment]
