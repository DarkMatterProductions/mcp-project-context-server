# ADR-00007: Chunking strategy for markdown indexing

## Status
Under Review

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

Heading-boundary splitting with a fixed-size fallback is the leading candidate for replacing the current fixed-size approach. The argument is straightforward: since all documents are markdown and the ADR template defines a consistent heading structure, splitting on headings produces chunks that align with the semantic units a user would actually want to retrieve (a full `## Decision` section, a full `## Consequences` section, etc.).

The primary concern is unbounded section length. A detailed `## Context` section in a complex ADR could be several thousand characters. The proposed mitigation is a two-pass approach: split on headings first; if any chunk exceeds a configurable `MAX_CHUNK_SIZE` (proposed: 2000 characters), apply fixed-size sub-chunking within that chunk, preserving the heading as a prefix for each sub-chunk.

Open questions before this ADR can move to Accepted:

1. What is the right `MAX_CHUNK_SIZE` threshold for the fallback? Should it match the current 1000-character limit or be larger (since heading-boundary chunks are more semantically coherent)?
2. Should the heading hierarchy be flattened (split on any `#`/`##`/`###`) or only on top-level sections (`##`)? Sub-headings within a section may be too granular.
3. How should the heading text be preserved in the chunk? Including the heading as the first line of the chunk provides context for retrieval but increases chunk size.
4. Should this change require a breaking migration note (existing indexed collections used fixed-size; users must re-index after upgrading)?

## Decision

TBD — pending resolution of the open questions above.

## Consequences

TBD

## Alternatives Considered

- **Fixed-size only (current)**: Simple, no dependencies, predictable. Semantically blind to markdown structure. Appropriate as a starting point but suboptimal for a server that exclusively indexes markdown files.
- **Sentence-boundary splitting**: Requires an NLP library (`spacy` or `nltk`), adding a heavyweight dependency. Benefit over heading-boundary splitting is marginal for the document types this server indexes.
- **Overlapping windows**: Increases storage requirements and introduces duplicate chunks in retrieval results. Does not address the core problem of slicing through semantically coherent sections.
