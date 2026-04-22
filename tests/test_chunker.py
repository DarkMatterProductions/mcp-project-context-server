"""Unit tests for the heading-boundary markdown chunker (ADR-00007)."""

from mcp_project_context_server.indexing.chunker import chunk_markdown

MAX = 1500  # default max_chunk_size


class TestChunkMarkdownEmptyInput:
    def test_empty_string_returns_empty_list(self):
        assert chunk_markdown("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert chunk_markdown("   \n\n  ") == []


class TestChunkMarkdownNoHeadings:
    def test_short_file_no_headings_is_single_chunk(self):
        text = "# Project Title\n\nSome introductory text.\n\nAnother paragraph."
        result = chunk_markdown(text, MAX)
        assert len(result) == 1
        assert "Some introductory text" in result[0]

    def test_oversized_no_headings_sub_splits_on_paragraphs(self):
        # Build a text with no ## headings but multiple paragraphs > MAX
        para = "A" * 400
        text = "\n\n".join([para] * 6)  # ~2400+ chars with separators
        result = chunk_markdown(text, MAX)
        assert len(result) > 1
        for chunk in result:
            # Each chunk should be <= MAX or be a single paragraph that cannot split
            assert len(chunk) <= MAX or chunk.count("\n\n") == 0


class TestChunkMarkdownBasicSections:
    def _make_doc(self, sections: dict[str, str]) -> str:
        parts = ["# Top Level Title\n"]
        for heading, body in sections.items():
            parts.append(f"## {heading}\n\n{body}")
        return "\n\n".join(parts)

    def test_two_short_sections_produce_two_chunks(self):
        doc = self._make_doc({"Status": "Accepted", "Context": "Some background info."})
        result = chunk_markdown(doc, MAX)
        # Preamble (# title) + 2 sections
        assert len(result) == 3
        headings = [c.split("\n")[0] for c in result]
        assert any("## Status" in h for h in headings)
        assert any("## Context" in h for h in headings)

    def test_heading_preserved_as_first_line(self):
        doc = "## Decision\n\nWe chose ChromaDB because it is embedded."
        result = chunk_markdown(doc, MAX)
        assert len(result) == 1
        assert result[0].startswith("## Decision")

    def test_multiple_sections_each_get_own_chunk(self):
        sections = {
            "Status": "Accepted",
            "Context": "Background.",
            "Decision": "We chose X.",
            "Consequences": "Things happened.",
            "Alternatives Considered": "We looked at Y.",
        }
        doc = self._make_doc(sections)
        result = chunk_markdown(doc, MAX)
        # 1 preamble + 5 sections
        assert len(result) == 6


class TestChunkMarkdownOversizedSections:
    def test_oversized_section_splits_on_blank_lines(self):
        # Build a section with multiple paragraphs that together exceed MAX
        paragraphs = ["Paragraph number {}: {}".format(i, "x" * 300) for i in range(6)]
        body = "\n\n".join(paragraphs)
        doc = f"## Context\n\n{body}"
        result = chunk_markdown(doc, MAX)
        assert len(result) > 1
        for chunk in result:
            # All chunks should be within MAX or be single unsplittable paragraphs
            assert len(chunk) <= MAX or "\n\n" not in chunk

    def test_oversized_section_with_h3_splits_on_h3(self):
        # Body has no blank-line-based split opportunity but has ### headings
        h3_body = "\n\n".join(
            [f"### Sub {i}\n\n{'Word ' * 100}" for i in range(5)]
        )
        doc = f"## Alternatives Considered\n\n{h3_body}"
        result = chunk_markdown(doc, MAX)
        assert len(result) > 1

    def test_single_giant_paragraph_kept_intact(self):
        # One continuous block, no breaks, no ### headings — must be kept as-is
        body = "A" * 3000
        doc = f"## Context\n\n{body}"
        result = chunk_markdown(doc, MAX)
        assert len(result) == 1
        assert len(result[0]) > MAX  # oversized but intact


class TestChunkMarkdownContentIntegrity:
    def test_no_content_lost(self):
        doc = (
            "# Title\n\n"
            "Preamble text.\n\n"
            "## Status\n\nAccepted\n\n"
            "## Context\n\nSome context.\n\n"
            "## Decision\n\nWe decided."
        )
        result = chunk_markdown(doc, MAX)
        combined = " ".join(result)
        assert "Preamble text" in combined
        assert "Accepted" in combined
        assert "Some context" in combined
        assert "We decided" in combined

    def test_empty_section_body_produces_heading_only_chunk(self):
        doc = "## Status\n\n## Context\n\nSome context."
        result = chunk_markdown(doc, MAX)
        headings = [c.split("\n")[0] for c in result]
        assert "## Status" in headings

    def test_chunks_are_non_empty_strings(self):
        doc = "## Section\n\nContent here.\n\n## Empty\n\n\n\n## Final\n\nMore content."
        result = chunk_markdown(doc, MAX)
        for chunk in result:
            assert chunk.strip() != ""


