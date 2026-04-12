"""Indexes .context/ files into ChromaDB for semantic search."""

import sys
from pathlib import Path

from project_context_server.integrations.chroma.client import chroma_client
from project_context_server.indexing.ollama.embedder import embed_chunk
from project_context_server.helpers.context import (
    find_context_dir,
    read_context_files,
    collection_name_for,
)


def index_project_context(project_path: str | Path) -> str:
    """Chunk, embed, and store all .context/ markdown files for a project."""
    context_dir = find_context_dir(project_path)
    if not context_dir:
        return f"No .context/ directory found at or above {project_path}"

    col_name = collection_name_for(context_dir)

    # Drop and recreate for a clean re-index
    try:
        chroma_client.delete_collection(col_name)
    except Exception:
        pass
    collection = chroma_client.create_collection(col_name)

    files = read_context_files(context_dir)
    indexed = 0

    for filename, file_content in files.items():
        # Chunk large files (e.g. BUNDLE.md) into 1000-char segments
        chunks = [file_content[i:i + 1000] for i in range(0, len(file_content), 1000)]
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            doc_id = f"{filename}::{i}"
            try:
                embedding = embed_chunk(chunk)
                collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"file": filename, "chunk": i}],
                )
                indexed += 1
            except Exception as e:
                print(f"Warning: failed to index {doc_id}: {e}", file=sys.stderr)

    return f"Indexed {indexed} chunks from {len(files)} files into collection '{col_name}'"