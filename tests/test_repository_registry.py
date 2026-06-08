"""Tests for the repository provider registry."""

import os

import pytest

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import (
    get_repository_provider,
    reset_provider_for_testing,
    validate_repo_access,
)


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the registry singleton before and after every test."""
    reset_provider_for_testing()
    yield
    reset_provider_for_testing()


class TestGetRepositoryProvider:
    """Tests for get_repository_provider() factory behaviour."""

    def test_defaults_to_local(self, monkeypatch):
        monkeypatch.delenv("REPO_PROVIDER", raising=False)
        from mcp_project_context_server.integrations.repository.local.client import (
            LocalRepositoryProvider,
        )

        provider = get_repository_provider()
        assert isinstance(provider, LocalRepositoryProvider)

    def test_returns_local_provider(self, monkeypatch):
        monkeypatch.setenv("REPO_PROVIDER", "local")
        from mcp_project_context_server.integrations.repository.local.client import (
            LocalRepositoryProvider,
        )

        provider = get_repository_provider()
        assert isinstance(provider, LocalRepositoryProvider)

    def test_returns_github_provider(self, monkeypatch):
        monkeypatch.setenv("REPO_PROVIDER", "github")
        from mcp_project_context_server.integrations.repository.github.client import (
            GitHubRepositoryProvider,
        )

        provider = get_repository_provider()
        assert isinstance(provider, GitHubRepositoryProvider)

    def test_returns_gitlab_provider(self, monkeypatch):
        monkeypatch.setenv("REPO_PROVIDER", "gitlab")
        from mcp_project_context_server.integrations.repository.gitlab.client import (
            GitLabRepositoryProvider,
        )

        provider = get_repository_provider()
        assert isinstance(provider, GitLabRepositoryProvider)

    def test_returns_gitea_provider(self, monkeypatch):
        monkeypatch.setenv("REPO_PROVIDER", "gitea")
        monkeypatch.setenv("REPO_BASE_URL", "https://gitea.example.com")
        from mcp_project_context_server.integrations.repository.gitea.client import (
            GiteaRepositoryProvider,
        )

        provider = get_repository_provider()
        assert isinstance(provider, GiteaRepositoryProvider)

    def test_raises_on_unknown_provider(self, monkeypatch):
        monkeypatch.setenv("REPO_PROVIDER", "unknown_provider")
        with pytest.raises(EnvironmentError, match="Unsupported REPO_PROVIDER"):
            get_repository_provider()

    def test_caches_singleton(self, monkeypatch):
        monkeypatch.setenv("REPO_PROVIDER", "local")
        p1 = get_repository_provider()
        p2 = get_repository_provider()
        assert p1 is p2

    def test_reset_clears_cache(self, monkeypatch):
        monkeypatch.setenv("REPO_PROVIDER", "local")
        p1 = get_repository_provider()
        reset_provider_for_testing()
        p2 = get_repository_provider()
        assert p1 is not p2


class TestMultiTenant:
    """Tests for multi-tenant mode behaviour."""

    def test_raises_if_multi_tenant_but_no_allowlists(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.delenv("APPROVED_ORGS", raising=False)
        monkeypatch.delenv("APPROVED_REPOS", raising=False)
        with pytest.raises(EnvironmentError, match="APPROVED_ORGS or APPROVED_REPOS"):
            get_repository_provider()

    def test_validate_passes_for_approved_org_member(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "myorg")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)
        get_repository_provider()
        # Should not raise
        validate_repo_access("myorg/some-repo")

    def test_validate_passes_for_approved_repo(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.delenv("APPROVED_ORGS", raising=False)
        monkeypatch.setenv("APPROVED_REPOS", "myorg/specific-repo")
        get_repository_provider()
        # Should not raise
        validate_repo_access("myorg/specific-repo")

    def test_validate_raises_for_unapproved_repo(self, monkeypatch):
        monkeypatch.setenv("REPO_MULTI_TENANT", "true")
        monkeypatch.setenv("APPROVED_ORGS", "myorg")
        monkeypatch.delenv("APPROVED_REPOS", raising=False)
        get_repository_provider()
        with pytest.raises(RepositoryError, match="not permitted"):
            validate_repo_access("otherapg/evil-repo")

    def test_validate_noop_in_single_tenant(self, monkeypatch):
        monkeypatch.delenv("REPO_MULTI_TENANT", raising=False)
        get_repository_provider()
        # Should not raise, regardless of repo_id
        validate_repo_access("any/repo")
        validate_repo_access("whatever/whatever")
