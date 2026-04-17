"""ChromaDB client configuration and singleton."""

import os
from pathlib import Path

import chromadb
from chromadb.config import Settings

_chroma_default: Path = Path.home() / ".mcp-data" / "chroma"
CHROMA_DIR: Path = Path(os.getenv("CHROMA_DIR", str(_chroma_default)))
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# chromadb.PersistentClient requires a str — this is the only place a Path is
# explicitly converted to str, at the external API boundary.
chroma_client: chromadb.ClientAPI = chromadb.PersistentClient(
    path=str(CHROMA_DIR),
    settings=Settings(anonymized_telemetry=False),
)
