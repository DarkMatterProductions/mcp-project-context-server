"""Heading-boundary markdown chunker with intelligent sub-splitting.

Strategy (ADR-00007):
- Split on top-level sections (## headings) only.
- Preserve heading text as the first line of each chunk.
- For sections exceeding MAX_CHUNK_SIZE:
    1. Split at blank-line paragraph boundaries.
    2. Fall back to ### sub-headings within the section.
    3. Allow oversized chunks as absolute last resort.
- Files with no ## headings are treated as a single chunk (sub-split if oversized).
"""

import re

# Regex that matches a ## heading line (not ### or deeper)
_H2_RE = re.compile(r"^(## .+)$", re.MULTILINE)
_H3_RE = re.compile(r"^(### .+)$", re.MULTILINE)


def _sub_split_by_paragraphs(text: str, max_size: int) -> list[str]:
    """Split *text* on blank lines into pieces no larger than *max_size*.

    Adjacent paragraphs are greedily merged until the next paragraph would
    exceed the limit.  If a single paragraph is itself larger than *max_size*
    it is kept intact (caller's last-resort logic handles it).
    """
    paragraphs = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    current_parts: list[str] = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        addition = len(para) + (2 if current_parts else 0)  # "\n\n" separator
        if current_parts and current_len + addition > max_size:
            chunks.append("\n\n".join(current_parts))
            current_parts = [para]
            current_len = len(para)
        else:
            current_parts.append(para)
            current_len += addition

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks


def _sub_split_by_h3(text: str, max_size: int) -> list[str]:
    """Split *text* on ### headings and then greedily merge small pieces."""
    parts = _H3_RE.split(text)
    # _H3_RE.split returns: [pre, heading1, body1, heading2, body2, ...]
    # Reassemble heading + body pairs
    sections: list[str] = []
    if parts[0].strip():
        sections.append(parts[0].strip())
    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()
        body = parts[i + 1].strip()
        sections.append(f"{heading}\n\n{body}" if body else heading)
        i += 2

    chunks: list[str] = []
    current_parts: list[str] = []
    current_len = 0

    for section in sections:
        addition = len(section) + (2 if current_parts else 0)
        if current_parts and current_len + addition > max_size:
            chunks.append("\n\n".join(current_parts))
            current_parts = [section]
            current_len = len(section)
        else:
            current_parts.append(section)
            current_len += addition

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks


def _split_section(heading: str, body: str, max_size: int) -> list[str]:
    """Return one or more chunks for a single ## section.

    The heading is prepended to the first chunk produced.
    """
    full = f"{heading}\n\n{body}".strip() if body.strip() else heading.strip()

    if len(full) <= max_size:
        return [full]

    # --- Pass 1: paragraph boundaries ---
    para_chunks = _sub_split_by_paragraphs(full, max_size)
    if all(len(c) <= max_size for c in para_chunks) and len(para_chunks) > 1:
        return para_chunks

    # --- Pass 2: ### sub-headings ---
    if _H3_RE.search(full):
        h3_chunks = _sub_split_by_h3(full, max_size)
        if all(len(c) <= max_size for c in h3_chunks) and len(h3_chunks) > 1:
            return h3_chunks

    # --- Last resort: return oversized chunk intact ---
    return [full]


def chunk_markdown(text: str, max_chunk_size: int = 1500) -> list[str]:
    """Split *text* into semantically coherent chunks.

    Parameters
    ----------
    text:
        Raw markdown content of a single file.
    max_chunk_size:
        Target maximum character length per chunk.  Chunks may exceed this
        only when no natural split point exists within a section.

    Returns
    -------
    list[str]
        Non-empty chunk strings ready for embedding.
    """
    if not text or not text.strip():
        return []

    # Split on ## headings; re.split with a capturing group keeps delimiters.
    parts = _H2_RE.split(text)
    # parts[0] is content before the first ## heading (preamble / # title block)
    # then alternates: heading, body, heading, body, ...

    chunks: list[str] = []

    # Handle preamble (content before the first ## heading, e.g. # Title line)
    preamble = parts[0].strip()
    if preamble:
        chunks.extend(_split_section(preamble, "", max_chunk_size))

    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()      # the ## Heading text
        body = parts[i + 1].strip()    # content until next ## heading
        chunks.extend(_split_section(heading, body, max_chunk_size))
        i += 2

    return [c for c in chunks if c.strip()]

