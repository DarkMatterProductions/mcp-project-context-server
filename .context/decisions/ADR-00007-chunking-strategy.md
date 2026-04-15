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

## ADR Review Discussion

Heading-boundary splitting with intelligent sub-splitting is the leading candidate for replacing the current fixed-size approach. The argument is straightforward: since all documents are markdown and the ADR template defines a consistent heading structure, splitting on headings produces chunks that align with the semantic units a user would actually want to retrieve (a full `## Decision` section, a full `## Consequences` section, etc.).

The primary concern is unbounded section length. A detailed `## Context` section in a complex ADR could be several thousand characters. The mitigation is a two-pass approach: split on headings first; if any chunk exceeds a configurable `MAX_CHUNK_SIZE` (proposed: 1500 characters), apply intelligent sub-splitting within that chunk rather than fixed-size sub-chunking.

Open questions before this ADR can move to Accepted:

1. **What is the right `MAX_CHUNK_SIZE` threshold for intelligent sub-splitting?**

   **Recommendation**: `MAX_CHUNK_SIZE` = 1500 characters (configurable via `CHUNK_SIZE` env var).

   **Implementation**: For oversized sections (> `MAX_CHUNK_SIZE`):
    1. Look for natural break points: list items, blank lines, topic shifts, horizontal rules
    2. Split at natural breaks where possible
    3. If no natural breaks, split on the next `###` heading within the section
    4. Only as absolute last resort, if a section cannot be meaningfully subdivided, allow it to exceed the limit

2. **Should the heading hierarchy be flattened (split on any `#`/`##`/`###`) or only on top-level sections (`##`)?**

   **Recommendation**: **Split on top-level sections (`##`) only**:
    - Aligns with the ADR template structure
    - Provides one chunk per logical unit of information
    - Avoids over-fragmentation from subsections
    - We can always add support for `###` levels later if needed

3. **How should the heading text be preserved in the chunk?**

   **Recommendation**: **Include the heading text as the first line of each chunk**:
    - Format: `## Heading Title\n\n{content}`
    - Provides immediate semantic context for retrieval
    - Minimal overhead for chunk size
    - Essential for distinguishing between similarly-sized sections
    - Preserve the heading hierarchy in the chunk content (not flattened)

4. **How should users be notified of the migration requirement?**

   **Recommendation**: **Notify via `load_project_context` output**:
    - Since `load_project_context` is the primary tool users call to retrieve context, it's the ideal place to surface migration messages
    - When the system detects that the indexed collection was built with the old chunking strategy (fixed 1000-char chunks), `load_project_context` will prepend a migration notice to its output
    - The notice will recommend running `index_project_context` to rebuild with the new heading-boundary strategy
    - This approach avoids requiring users to track ADR changes separately
    - The notice can be versioned/stable so users see it only once per project after re-indexing

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

**Migration:**
- This is a breaking change requiring a full re-index
- Users are notified to run `index_project_context` after upgrading
- Old collections are preserved until explicitly rebuilt

**Versioning Strategy:**
- The server version is defined in `pyproject.toml` under the `project.version` field (currently `0.2.2`)
- The version is programmatically accessible via `importlib.metadata.version(__name__)` in Python code
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
- **Code changes required**: `indexing/chroma/indexer.py` will be refactored to implement heading-boundary splitting with intelligent sub-splitting
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
