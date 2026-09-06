# ADR-00007: Chunking strategy for markdown indexing

## Status
Accepted

## Context

All documents consumed by this server are `.md` files — project overviews, ADRs, and session notes. Before embedding, each file must be split into chunks that fit within the embedding model's context window and represent semantically coherent units of information for retrieval.

The current implementation uses **fixed 1000-character non-overlapping chunks**. This is a simple, universal strategy but it is semantically blind — it slices through ADR sections (e.g., mid-way through `## Context` or `## Decision`) without regard for document structure.

Since all indexed documents are markdown, the document structure is available for use in chunking. The key structural element is the heading hierarchy (`#`, `##`, `###`). Every ADR section (`## Status`, `## Context`, `## Decision`, `## Consequences`, `## Alternatives Considered`) is a natural, self-contained unit of meaning. Keeping these sections intact during chunking would improve retrieval precision — a search for "why was ChromaDB chosen" would return the full `## Decision` section of ADR-00002 rather than an arbitrary 1000-character slice that may cut the reasoning in half.

Options under consideration:

- **Fixed-size (current)**: Split every N characters regardless of structure. Simple. Predictable chunk count. Semantically blind.
- **Heading-boundary**: Split on markdown headings (`#`, `##`, `###`). Keeps sections intact. Variable chunk size — some sections may be very short (e.g., `## Status\nAccepted`), others arbitrarily long. Requires a fallback strategy for oversized sections.
- **Heading-boundary with fixed-size fallback**: Split on headings first. If any resulting section exceeds a configurable maximum (e.g., 2000 characters), apply fixed-size sub-chunking within that section. Combines the semantic coherence of heading-boundary splitting with a size bound guarantee.
- **Sentence-boundary**: Split on sentence terminators. More granular than headings. Requires an NLP library (e.g., `spacy`, `nltk`) — a significant dependency addition for marginal benefit over heading-boundary.
- **Overlapping windows**: Fixed-size windows with overlap (e.g., 1000 chars with 200-char overlap). Reduces the chance of a relevant passage being split across chunk boundaries. Produces duplicate content in retrieval results and increases storage size.

## Decision

Proceed with heading-boundary chunking as the new strategy, subject to implementation of intelligent sub-splitting for oversized sections.

**Configuration:**
- `MAX_CHUNK_SIZE` = 1500 characters (configurable via `CHUNK_SIZE` env var)
- Split on top-level headings (`##`) only
- Preserve heading text as first line of each chunk
- For chunks exceeding `MAX_CHUNK_SIZE`, apply intelligent sub-splitting:
    1. Look for natural break points (lists, blank lines, topic shifts)
    2. Split at natural breaks
    3. Fall back to `###` headings if available
    4. Allow oversized chunks as last resort

**Chunk metadata:**
- In addition to the existing `file`/`chunk` fields, each chunk's metadata gains:
  - `section` — the top-level heading text the chunk belongs to (e.g. `"Decision"`), stored as structured metadata rather than only as the chunk-content prefix. This lets section-scoped tools (e.g. ADR-00012's `search_adr_sections`) filter by section without re-parsing chunk content.
  - `section_sha512` — the SHA-512 hex digest of the section's raw content, computed with the existing `hash_content()` helper (`helpers/context_files.py`) already used for whole-file hashing in `load_context_files`. This allows a caller to detect whether a specific section has changed by comparing digests, without diffing content or re-hashing the whole file.

**Migration:**
- This is a breaking change requiring a full re-index
- Users are notified to run `index_project_context` after upgrading
- Old collections are preserved until explicitly rebuilt

**Versioning Strategy:**
- The server version is defined in `pyproject.toml` via a dynamic `project.version` field and is programmatically accessible via `importlib.metadata.version(__name__)` in Python code — no version number is hardcoded in this ADR or in the implementation
- Each ChromaDB collection stores a `server_version` field in its metadata, initialized from the server version
- Implementation details:
  - On collection creation/update: write the current server version to the collection's `server_version` metadata field
  - On `load_project_context`: use `importlib.metadata.version(__name__)` to get the current server version
  - Compare the collection's `server_version` against the current server version obtained via `importlib.metadata.version()`
  - If versions mismatch: prepend migration notice to `load_project_context` output and recommend running `index_project_context`
  - If versions match: return normal results without migration notice
  - After successful `index_project_context`: the collection's `server_version` is synchronized to the current server version

## Consequences

- **Improved retrieval precision**: Search queries will match complete semantic sections rather than arbitrary slices
- **Better context for embeddings**: Each chunk contains a coherent unit of information with clear boundaries
- **Intelligent handling of large sections**: Complex ADRs with lengthy context sections are handled by finding natural breaks within the section
- **Breaking change**: Existing indexed collections will be rebuilt with the new strategy. Users must re-index after upgrading.
- **Configurable chunk size**: The `CHUNK_SIZE` environment variable controls the maximum chunk size before sub-splitting
- **Intelligent sub-splitting**: Large sections are intelligently divided rather than arbitrarily sliced
- **Migration notification**: Users are informed via `load_project_context` output without needing to track ADR changes
- **Code changes required**: `indexing/indexer.py` (`run_index_pipeline`) will be updated to implement heading-boundary splitting with intelligent sub-splitting. Note: `indexing/chroma/indexer.py` is deprecated — all chunking work targets the provider-agnostic `indexing/indexer.py`.
- **`section` metadata required by ADR-00012**: ADR-00012's `search_adr_sections` tool depends on each chunk's metadata carrying a `section` field so it can filter results to a single ADR section without re-parsing heading text out of chunk content.
- **Cheap per-section change detection**: The `section_sha512` metadata field lets a caller compare digests to determine whether a specific section's content has changed, without diffing content or re-hashing the whole file. This reuses the existing `hash_content()` helper (`helpers/context_files.py`) rather than introducing new hashing logic.
- **Migration tracking**: System must track collection version to determine when to show migration notice
  - Collection metadata stores `server_version` field (server version from `pyproject.toml`)
  - On each collection update, store current server version (via `importlib.metadata.version()`) in metadata
  - On `load_project_context`, compare collection's `server_version` against current server version (obtained via `importlib.metadata.version()`)
  - When versions mismatch, prepend migration notice + recommend running `index_project_context`
  - After successful re-index, collection's `server_version` is synchronized to current server version
  - Server version is read using `importlib.metadata.version(__name__)` from `pyproject.toml`

## Alternatives Considered

- **Fixed-size only (current)**: Rejected. Semantically blind, produces arbitrary slices through semantic units. Inappropriate for a server that exclusively indexes markdown files with consistent heading structure.
- **Sentence-boundary splitting**: Rejected. Requires NLP library (`spacy` or `nltk`), adding heavyweight dependency. Benefit over heading-boundary splitting is marginal for markdown documents.
- **Overlapping windows**: Rejected. Increases storage requirements and introduces duplicate chunks. Does not address the core problem of slicing through semantically coherent sections.
- **Fixed-size fallback retained (initial proposal)**: Rejected after discussion. Retaining fixed-size chunking undermines the semantic benefits of heading-boundary splitting and creates inconsistency. Intelligent sub-splitting is a better approach for handling oversized sections.
- **Flattened heading hierarchy (split on `#`, `##`, `###`)**: Rejected. Sub-headings within a section are too granular and should remain part of the same semantic unit. Top-level sections (`##`) provide appropriate chunk boundaries.
- **No migration tracking**: Rejected. Relying on user to track ADR changes is unreliable and poor UX. Automatic notification via `load_project_context` is the only acceptable approach.
