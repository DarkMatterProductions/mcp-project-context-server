"""Tests for RepositoryProvider Protocol, RepositoryInfo dataclass, and RepositoryError."""

import pytest

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    RepositoryProvider,
    normalize_repo_identifier,
)


class TestRepositoryInfo:
    """Tests for the RepositoryInfo dataclass."""

    def test_required_fields(self):
        info = RepositoryInfo(identifier="org/repo", name="repo", description="A repo", indexed=False)
        assert info.identifier == "org/repo"
        assert info.name == "repo"
        assert info.description == "A repo"
        assert info.indexed is False
        assert info.last_indexed is None

    def test_last_indexed_can_be_set(self):
        info = RepositoryInfo(
            identifier="org/repo",
            name="repo",
            description="",
            indexed=True,
            last_indexed="2024-01-15T12:00:00",
        )
        assert info.indexed is True
        assert info.last_indexed == "2024-01-15T12:00:00"


class TestRepositoryError:
    """Tests for the RepositoryError exception."""

    def test_is_exception(self):
        err = RepositoryError("something went wrong")
        assert isinstance(err, Exception)
        assert str(err) == "something went wrong"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(RepositoryError, match="oops"):
            raise RepositoryError("oops")


class TestRepositoryProviderProtocol:
    """Tests for Protocol conformance checking."""

    def test_concrete_implementation_satisfies_protocol(self):
        """A class implementing all required methods satisfies the Protocol."""

        class FakeProvider:
            @property
            def provider_name(self) -> str:
                return "fake"

            async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
                return {}

            async def fetch_source_bundle(self, repo_id: str):
                return None

            async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
                return {}

            async def write_file(self, repo_id: str, path: str, content: str, message: str, branch=None) -> None:
                pass

            async def create_branch(self, repo_id: str, new_branch: str, from_branch=None) -> None:
                pass

            async def get_default_branch(self, repo_id: str) -> str:
                return "main"

            async def list_repositories(self, org=None):
                return []

        provider = FakeProvider()
        assert isinstance(provider, RepositoryProvider)

    def test_incomplete_implementation_does_not_satisfy_protocol(self):
        """A class missing required methods does not satisfy the Protocol."""

        class IncompleteProvider:
            async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
                return {}

        provider = IncompleteProvider()
        assert not isinstance(provider, RepositoryProvider)


class TestNormalizeRepoIdentifier:
    """Tests for the shared normalize_repo_identifier helper."""

    def test_passthrough_owner_repo(self):
        assert normalize_repo_identifier("owner/repo") == "owner/repo"

    def test_normalises_https_url(self):
        assert normalize_repo_identifier("https://github.com/owner/repo") == "owner/repo"

    def test_normalises_http_url(self):
        assert normalize_repo_identifier("http://gitea.example.com/owner/repo") == "owner/repo"

    def test_normalises_url_with_trailing_slash(self):
        assert normalize_repo_identifier("https://gitlab.com/owner/repo/") == "owner/repo"

    def test_normalises_nested_gitlab_group_url(self):
        assert normalize_repo_identifier("https://gitlab.com/acme/team/backend") == "team/backend"
