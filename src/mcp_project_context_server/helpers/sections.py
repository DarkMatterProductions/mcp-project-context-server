"""Heading-boundary markdown splitting, shared by the indexer and (future) ADR section tools.

Implements the chunking strategy from ADR-00007: split on top-level (``##``)
headings only, preserving heading text as the first line of each resulting
chunk, with a staged fallback for sections that exceed a caller-supplied
maximum size (natural paragraph breaks, then ``###`` sub-headings, then
allowing an oversized chunk as a last resort).
"""
import re
from dataclasses import dataclass

_TOP_HEADING_RE = re.compile(r"^##(?!#)[ \t]+(.*)$", re.MULTILINE)
_SUB_HEADING_RE = re.compile(r"^###(?!#)[ \t]+.*$", re.MULTILINE)
_TITLE_RE = re.compile(r"^#(?!#)[ \t]+(.*)$", re.MULTILINE)


@dataclass
class Section:
    """One top-level (``##``) section of a markdown document.

    :ivar name: The heading text, or the document's ``#`` title (or ``""``)
        for content preceding the first ``##`` heading.
    :ivar content: The section's raw content, with its heading line (if any)
        included as the first line.
    """

    name: str
    content: str


def split_sections(text: str) -> list[Section]:
    """Split *text* into `Section`s on top-level (``##``) headings only.

    Content preceding the first ``##`` heading (e.g. an ADR's ``# Title``
    line) becomes its own leading `Section`, named from the document's ``#``
    title line if present, else ``""``. It is omitted if blank.

    :param text: (str) The full markdown document content.
    :return: (list) `Section`s in document order.
    """
    matches = list(_TOP_HEADING_RE.finditer(text))
    sections: list[Section] = []

    preamble_end = matches[0].start() if matches else len(text)
    preamble = text[:preamble_end]
    if preamble.strip():
        title_match = _TITLE_RE.search(preamble)
        preamble_name = title_match.group(1).strip() if title_match else ""
        sections.append(Section(name=preamble_name, content=preamble))

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append(Section(name=match.group(1).strip(), content=text[start:end]))

    return sections


def _pack_paragraphs(paragraphs: list[str], max_chars: int, sep: str) -> list[str]:
    """Greedily pack *paragraphs* into pieces no longer than *max_chars* where possible."""
    pieces: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        added_len = len(para) if not current else len(para) + len(sep)
        if current and current_len + added_len > max_chars:
            pieces.append(sep.join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += added_len

    if current:
        pieces.append(sep.join(current))

    return pieces


def _split_oversized(body: str, max_chars: int) -> list[str]:
    """Apply the staged natural-break -> ``###`` -> oversized-fallback split to *body*."""
    paragraphs = re.split(r"\n\s*\n", body)
    pieces = _pack_paragraphs(paragraphs, max_chars, sep="\n\n")

    result: list[str] = []
    for piece in pieces:
        if len(piece) <= max_chars:
            result.append(piece)
            continue

        sub_matches = list(_SUB_HEADING_RE.finditer(piece))
        if not sub_matches:
            result.append(piece)
            continue

        sub_pieces: list[str] = []
        first_start = sub_matches[0].start()
        if piece[:first_start].strip():
            sub_pieces.append(piece[:first_start])
        for i, match in enumerate(sub_matches):
            start = match.start()
            end = sub_matches[i + 1].start() if i + 1 < len(sub_matches) else len(piece)
            sub_pieces.append(piece[start:end])
        result.extend(sub_pieces)

    return result


def chunk_section(section: Section, max_chars: int) -> list[str]:
    """Split *section* into one or more chunk strings no longer than *max_chars*, where possible.

    A section within the limit is returned unchanged as a single chunk. An
    oversized section is split on paragraph boundaries first, falling back to
    ``###`` sub-headings for any still-oversized piece, and finally left
    oversized if no further natural break is available. Every returned chunk
    is prefixed with the section's heading line so heading text remains the
    first line of each chunk.

    :param section: (Section) The section to split.
    :param max_chars: (int) The target maximum chunk size in characters.
    :return: (list) One or more chunk strings, in document order.
    """
    if len(section.content) <= max_chars:
        return [section.content]

    heading_match = _TOP_HEADING_RE.match(section.content) or _TITLE_RE.match(section.content)
    if heading_match:
        heading_line = section.content[: heading_match.end()]
        body = section.content[heading_match.end() :].lstrip("\n")
    else:
        heading_line = f"## {section.name}" if section.name else ""
        body = section.content

    pieces = _split_oversized(body, max_chars)
    if not heading_line:
        return pieces

    return [f"{heading_line}\n\n{piece.strip()}" if piece.strip() else heading_line for piece in pieces]
