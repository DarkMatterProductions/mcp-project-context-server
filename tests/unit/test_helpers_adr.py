"""Tests for helpers/adr.py — ADR discovery, resolution, and section editing."""

import pytest

from mcp_project_context_server.helpers.adr import (
    find_section,
    list_adrs,
    parse_status,
    replace_section,
    resolve_adr,
)
from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing

_WELL_FORMED = """# ADR-00001: First Decision

## Status
Accepted

## Context
Some context.

## Decision
We decided X.

## Consequences
Things happen.
"""

_LEGACY = """# ADR-00002: Legacy Decision

**Status:** Accepted

Some legacy content without a Status heading.
"""


def _write_adr(context_dir, filename, content):
    decisions_dir = context_dir / "decisions"
    decisions_dir.mkdir(exist_ok=True)
    (decisions_dir / filename).write_text(content, encoding="utf-8")


class TestListAdrs:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_lists_well_formed_adrs_sorted_by_number(self, tmp_path):
        project_dir = tmp_path / "project"
        context_dir = project_dir / ".context"
        context_dir.mkdir(parents=True)
        _write_adr(context_dir, "ADR-00002-second.md", _WELL_FORMED.replace("00001", "00002"))
        _write_adr(context_dir, "ADR-00001-first.md", _WELL_FORMED)

        infos, warnings = await list_adrs(str(project_dir))

        assert [info.number for info in infos] == [1, 2]
        assert infos[0].title == "First Decision"
        assert infos[0].status == "Accepted"
        assert infos[0].malformed is False
        assert warnings == []

    @pytest.mark.asyncio
    async def test_flags_legacy_format_as_malformed(self, tmp_path):
        project_dir = tmp_path / "project"
        context_dir = project_dir / ".context"
        context_dir.mkdir(parents=True)
        _write_adr(context_dir, "ADR-00002-legacy.md", _LEGACY)

        infos, warnings = await list_adrs(str(project_dir))

        assert len(infos) == 1
        assert infos[0].malformed is True
        assert infos[0].status == ""

    @pytest.mark.asyncio
    async def test_warns_on_non_conforming_filename(self, tmp_path):
        project_dir = tmp_path / "project"
        context_dir = project_dir / ".context"
        context_dir.mkdir(parents=True)
        _write_adr(context_dir, "not-an-adr.md", "# Not an ADR\n")

        infos, warnings = await list_adrs(str(project_dir))

        assert infos == []
        assert any("not-an-adr.md" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_empty_when_no_decisions_dir(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context").mkdir(parents=True)

        infos, warnings = await list_adrs(str(project_dir))

        assert infos == []
        assert warnings == []


class TestResolveAdr:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.fixture
    def project_dir(self, tmp_path):
        project_dir = tmp_path / "project"
        context_dir = project_dir / ".context"
        context_dir.mkdir(parents=True)
        _write_adr(context_dir, "ADR-00001-first.md", _WELL_FORMED)
        return project_dir

    @pytest.mark.asyncio
    async def test_resolve_by_int(self, project_dir):
        resolution = await resolve_adr(str(project_dir), 1)
        assert resolution.error is None
        assert resolution.info.number == 1
        assert "First Decision" in resolution.content

    @pytest.mark.asyncio
    async def test_resolve_by_numeric_string(self, project_dir):
        resolution = await resolve_adr(str(project_dir), "1")
        assert resolution.error is None
        assert resolution.info.filename == "ADR-00001-first.md"

    @pytest.mark.asyncio
    async def test_resolve_by_short_form_case_insensitive(self, project_dir):
        resolution = await resolve_adr(str(project_dir), "adr-00001")
        assert resolution.error is None
        assert resolution.info.number == 1

    @pytest.mark.asyncio
    async def test_resolve_by_exact_filename(self, project_dir):
        resolution = await resolve_adr(str(project_dir), "ADR-00001-first.md")
        assert resolution.error is None
        assert resolution.info.number == 1

    @pytest.mark.asyncio
    async def test_not_found_lists_known_adrs(self, project_dir):
        resolution = await resolve_adr(str(project_dir), 99)
        assert resolution.info is None
        assert resolution.content is None
        assert "No ADR found matching '99'" in resolution.error
        assert "ADR-00001" in resolution.error


class TestParseStatus:
    def test_finds_standard_status(self):
        status, found = parse_status(_WELL_FORMED)
        assert found is True
        assert status == "Accepted"

    def test_legacy_format_not_found(self):
        status, found = parse_status(_LEGACY)
        assert found is False
        assert status == ""


class TestFindSection:
    def test_finds_existing_section(self):
        section = find_section(_WELL_FORMED, "Decision")
        assert section is not None
        assert "We decided X." in section.content

    def test_returns_none_for_missing_section(self):
        assert find_section(_WELL_FORMED, "Nonexistent") is None


class TestReplaceSection:
    def test_replaces_middle_section_content(self):
        updated = replace_section(_WELL_FORMED, "Context", "New context body.")
        assert "New context body." in updated
        assert "Some context." not in updated
        assert "## Decision" in updated
        assert "We decided X." in updated

    def test_returns_none_for_missing_section(self):
        assert replace_section(_WELL_FORMED, "Nonexistent", "x") is None

    def test_preserves_trailing_newline_on_last_section(self):
        updated = replace_section(_WELL_FORMED, "Consequences", "New consequences.")
        assert updated.endswith("New consequences.\n")
