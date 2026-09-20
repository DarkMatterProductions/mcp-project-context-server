"""Tests for the update_adr_status tool — the full lifecycle transition matrix."""
from unittest.mock import AsyncMock, patch

import pytest

from mcp_project_context_server.integrations.repository.registry import reset_provider_for_testing
from mcp_project_context_server.tools.update_adr_status import handle


def _adr(status="Proposed", discussion="[Discussion pending]", decision="[Pending review]", number=1):
    return f"""# ADR-{number:05d}: Some Decision

## Status
{status}

## Context
Some context.

## ADR Review Discussion
{discussion}

## Decision
{decision}

## Consequences
[Pending review]

## Alternatives Considered
[Pending review]
"""


_LEGACY = """# ADR-00002: Legacy Decision

**Status:** Accepted

Legacy body.
"""


def _write(decisions_dir, filename, content):
    decisions_dir.mkdir(parents=True, exist_ok=True)
    (decisions_dir / filename).write_text(content, encoding="utf-8")


class TestUpdateAdrStatus:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_invalid_status_rejected(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        _write(decisions_dir, "ADR-00001-x.md", _adr())

        result = await handle(
            {"project_path": str(project_dir), "number_or_filename": 1, "new_status": "Bogus"}
        )

        assert "Invalid status 'Bogus'" in result[0].text

    @pytest.mark.asyncio
    async def test_no_op_when_status_unchanged(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        adr_file = decisions_dir / "ADR-00001-x.md"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Proposed"))

        result = await handle(
            {"project_path": str(project_dir), "number_or_filename": 1, "new_status": "Proposed"}
        )

        assert "already 'Proposed'" in result[0].text
        assert "No changes made" in result[0].text
        assert adr_file.read_text(encoding="utf-8") == _adr(status="Proposed")

    @pytest.mark.asyncio
    async def test_normal_forward_transition_without_explanation(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        adr_file = decisions_dir / "ADR-00001-x.md"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Proposed"))

        result = await handle(
            {"project_path": str(project_dir), "number_or_filename": 1, "new_status": "Under Review"}
        )

        content = adr_file.read_text(encoding="utf-8")
        assert "## Status\n\nUnder Review" in content
        assert "Update ADR-00001 status" in result[0].text or "Updated ADR-00001 status" in result[0].text

    @pytest.mark.asyncio
    async def test_unusual_transition_without_explanation_rejected(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Proposed"))

        result = await handle(
            {"project_path": str(project_dir), "number_or_filename": 1, "new_status": "Implemented"}
        )

        assert "unusual" in result[0].text
        assert "requires an 'explanation'" in result[0].text

    @pytest.mark.asyncio
    async def test_unusual_transition_with_explanation_succeeds(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        adr_file = decisions_dir / "ADR-00001-x.md"
        _write(
            decisions_dir,
            "ADR-00001-x.md",
            _adr(status="Accepted", discussion="prior discussion", decision="We decided X."),
        )

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "new_status": "Deprecated",
                "explanation": "No longer relevant.",
            }
        )

        content = adr_file.read_text(encoding="utf-8")
        assert "## Status\n\nDeprecated" in content
        assert "Updated ADR-00001 status" in result[0].text

    @pytest.mark.asyncio
    async def test_review_discussion_appended_when_proposed(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        adr_file = decisions_dir / "ADR-00001-x.md"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Proposed"))

        await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "new_status": "Under Review",
                "explanation": "Looks reasonable so far.",
            }
        )

        content = adr_file.read_text(encoding="utf-8")
        assert "[update_adr_status]:** Looks reasonable so far." in content

    @pytest.mark.asyncio
    async def test_review_discussion_removed_on_accepted(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        adr_file = decisions_dir / "ADR-00001-x.md"
        _write(
            decisions_dir,
            "ADR-00001-x.md",
            _adr(status="Under Review", discussion="Some discussion here.", decision="We decided X."),
        )

        result = await handle(
            {"project_path": str(project_dir), "number_or_filename": 1, "new_status": "Accepted"}
        )

        content = adr_file.read_text(encoding="utf-8")
        assert "## ADR Review Discussion" not in content
        assert "## Status\n\nAccepted" in content
        assert "Updated" in result[0].text

    @pytest.mark.asyncio
    async def test_accepted_requires_explanation_when_decision_is_placeholder(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        adr_file = decisions_dir / "ADR-00001-x.md"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Under Review", decision="[Pending review]"))

        result = await handle(
            {"project_path": str(project_dir), "number_or_filename": 1, "new_status": "Accepted"}
        )

        assert "requires a" in result[0].text
        assert "Decision section" in result[0].text
        content = adr_file.read_text(encoding="utf-8")
        assert "## Status\nUnder Review" in content

    @pytest.mark.asyncio
    async def test_accepted_with_explanation_populates_decision(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        adr_file = decisions_dir / "ADR-00001-x.md"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Under Review", decision="[Pending review]"))

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "new_status": "Accepted",
                "explanation": "We will go with option A.",
            }
        )

        content = adr_file.read_text(encoding="utf-8")
        assert "## Status\n\nAccepted" in content
        assert "We will go with option A." in content
        assert "## ADR Review Discussion" not in content
        assert "Updated" in result[0].text

    @pytest.mark.asyncio
    async def test_supersede_blocked_when_target_missing(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Accepted", decision="We decided X."))

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "new_status": "Superseded by ADR-00099",
                "explanation": "Superseded.",
            }
        )

        assert "ADR-00099 does not exist" in result[0].text

    @pytest.mark.asyncio
    async def test_supersede_succeeds_when_target_exists(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        adr_file = decisions_dir / "ADR-00001-x.md"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Accepted", decision="We decided X.", number=1))
        _write(decisions_dir, "ADR-00002-y.md", _adr(status="Proposed", number=2))

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "new_status": "Superseded by ADR-00002",
                "explanation": "Replaced by newer decision.",
            }
        )

        content = adr_file.read_text(encoding="utf-8")
        assert "## Status\n\nSuperseded by ADR-00002" in content
        assert "Updated" in result[0].text

    @pytest.mark.asyncio
    async def test_legacy_format_rejected(self, tmp_path):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        _write(decisions_dir, "ADR-00002-legacy.md", _LEGACY)

        result = await handle(
            {"project_path": str(project_dir), "number_or_filename": 2, "new_status": "Implemented"}
        )

        assert "legacy" in result[0].text.lower()
        assert "not supported" in result[0].text

    @pytest.mark.asyncio
    async def test_adr_not_found(self, tmp_path):
        project_dir = tmp_path / "project"
        (project_dir / ".context" / "decisions").mkdir(parents=True)

        result = await handle(
            {"project_path": str(project_dir), "number_or_filename": 99, "new_status": "Implemented"}
        )

        assert "No ADR found matching '99'" in result[0].text

    @pytest.mark.asyncio
    async def test_auto_reindex_runs_indexer(self, tmp_path, mocker):
        project_dir = tmp_path / "project"
        decisions_dir = project_dir / ".context" / "decisions"
        _write(decisions_dir, "ADR-00001-x.md", _adr(status="Proposed"))
        fake_index_result = [mocker.MagicMock(text="Indexed 1 file.")]
        mocker.patch(
            "mcp_project_context_server.tools.index_context.handle",
            new=AsyncMock(return_value=fake_index_result),
        )

        result = await handle(
            {
                "project_path": str(project_dir),
                "number_or_filename": 1,
                "new_status": "Under Review",
                "auto_reindex": True,
            }
        )

        assert "Indexed 1 file." in result[0].text

    @pytest.mark.asyncio
    async def test_blocked_by_allowlist(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "approved-org")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)

        result = await handle(
            {
                "project_path": "unapproved-org/some-repo",
                "number_or_filename": 1,
                "new_status": "Implemented",
            }
        )

        assert "not permitted" in result[0].text


class TestUpdateAdrStatusRemote:
    def teardown_method(self):
        reset_provider_for_testing()

    @pytest.mark.asyncio
    async def test_remote_status_update(self, monkeypatch):
        monkeypatch.setenv("REPO_ADR_WRITE_MODE", "direct")
        mock_provider = AsyncMock()
        mock_provider.provider_name = "github"
        mock_provider.fetch_context_files = AsyncMock(
            return_value={"decisions/ADR-00001-x.md": _adr(status="Proposed")}
        )
        mock_provider.get_default_branch = AsyncMock(return_value="main")

        with (
            patch(
                "mcp_project_context_server.helpers.context_files.get_repository_provider",
                return_value=mock_provider,
            ),
            patch(
                "mcp_project_context_server.tools.update_adr_status.get_repository_provider",
                return_value=mock_provider,
            ),
        ):
            result = await handle(
                {
                    "project_path": "owner/repo",
                    "number_or_filename": 1,
                    "new_status": "Under Review",
                }
            )

        mock_provider.write_file.assert_called_once()
        args, kwargs = mock_provider.write_file.call_args
        assert args[1] == ".context/decisions/ADR-00001-x.md"
        assert "## Status\n\nUnder Review" in args[2]
        assert "Wrote" in result[0].text
