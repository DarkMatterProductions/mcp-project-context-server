"""Tests for the heading-boundary markdown splitting helpers in helpers/sections.py."""

from mcp_project_context_server.helpers.sections import Section, chunk_section, split_sections


class TestSplitSections:
    def test_splits_on_top_level_headings_only(self):
        text = (
            "# ADR-00001: Title\n\n"
            "## Status\nAccepted\n\n"
            "## Context\nSome context.\n\n"
            "### Sub-heading\nNested detail, stays with Context.\n\n"
            "## Decision\nThe decision.\n"
        )

        sections = split_sections(text)

        assert [s.name for s in sections] == ["ADR-00001: Title", "Status", "Context", "Decision"]
        assert "### Sub-heading" in sections[2].content
        assert "The decision." in sections[3].content

    def test_preamble_named_from_title_line(self):
        text = "# ADR-00001: Title\n\nIntro text.\n\n## Status\nAccepted\n"

        sections = split_sections(text)

        assert sections[0].name == "ADR-00001: Title"
        assert sections[0].content.startswith("# ADR-00001: Title")

    def test_blank_preamble_is_omitted(self):
        text = "## Status\nAccepted\n\n## Context\nSome context.\n"

        sections = split_sections(text)

        assert [s.name for s in sections] == ["Status", "Context"]

    def test_preamble_without_title_line_named_empty_string(self):
        text = "Just some leading prose, no title.\n\n## Status\nAccepted\n"

        sections = split_sections(text)

        assert sections[0].name == ""
        assert "Just some leading prose" in sections[0].content

    def test_no_headings_returns_single_untitled_section(self):
        text = "Just a plain document with no headings at all."

        sections = split_sections(text)

        assert len(sections) == 1
        assert sections[0].name == ""
        assert sections[0].content == text

    def test_heading_text_is_stripped(self):
        text = "##   Spacey Heading   \nBody.\n"

        sections = split_sections(text)

        assert sections[0].name == "Spacey Heading"


class TestChunkSection:
    def test_section_within_limit_returned_unchanged(self):
        section = Section(name="Status", content="## Status\nAccepted\n")

        pieces = chunk_section(section, max_chars=1500)

        assert pieces == [section.content]

    def test_oversized_section_splits_on_paragraph_breaks(self):
        para_a = "A" * 40
        para_b = "B" * 40
        para_c = "C" * 40
        content = f"## Context\n{para_a}\n\n{para_b}\n\n{para_c}\n"
        section = Section(name="Context", content=content)

        pieces = chunk_section(section, max_chars=60)

        assert len(pieces) > 1
        for piece in pieces:
            assert piece.startswith("## Context")

    def test_oversized_paragraph_falls_back_to_sub_headings(self):
        sub_a = "### Sub A\n" + ("x" * 80)
        sub_b = "### Sub B\n" + ("y" * 80)
        content = f"## Context\n{sub_a}\n\n{sub_b}\n"
        section = Section(name="Context", content=content)

        pieces = chunk_section(section, max_chars=50)

        assert any("### Sub A" in piece for piece in pieces)
        assert any("### Sub B" in piece for piece in pieces)
        for piece in pieces:
            assert piece.startswith("## Context")

    def test_no_natural_break_allows_oversized_chunk_as_last_resort(self):
        body = "z" * 500
        content = f"## Context\n{body}\n"
        section = Section(name="Context", content=content)

        pieces = chunk_section(section, max_chars=50)

        assert len(pieces) == 1
        assert body in pieces[0]

    def test_section_without_heading_line_falls_back_to_name(self):
        # Simulates a preamble section with no literal "## " line in its content.
        body_a = "A" * 40
        body_b = "B" * 40
        section = Section(name="", content=f"{body_a}\n\n{body_b}")

        pieces = chunk_section(section, max_chars=45)

        assert len(pieces) > 1
        assert all("A" * 40 in piece or "B" * 40 in piece for piece in pieces)
