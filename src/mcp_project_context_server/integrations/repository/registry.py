"""Repository provider registry — factory driven by the ``REPO_PROVIDER`` env var.

Design rules
------------
* Defaults to ``"local"`` when ``REPO_PROVIDER`` is not set.
* **Fail fast** if the value is unrecognised.
* The returned instance is cached after the first call.
* Multi-tenant mode is activated by ``REPO_MULTI_TENANT=true``.

Usage
-----
::

    from mcp_project_context_server.integrations.repository.registry import (
        get_repository_provider,
        validate_repo_access,
    )

    provider = get_repository_provider()
    validate_repo_access("owner/repo")

Supported ``REPO_PROVIDER`` values
------------------------------------
``local``
    Local filesystem provider.

``github``
    GitHub / GitHub Enterprise.

``gitlab``
    GitLab / self-hosted GitLab.

``gitea``
    Self-hosted Gitea.  Requires ``REPO_BASE_URL``.

Multi-tenant mode (``REPO_MULTI_TENANT=true``)
----------------------------------------------
At least one of ``APPROVED_ORGS`` or ``APPROVED_REPOS`` must be set.
``validate_repo_access(repo_id)`` raises :exc:`RepositoryError` if the
repo identifier is not in any approved list.
"""

import os
from typing import Optional

from mcp_project_context_server.integrations.repository.base import RepositoryError, RepositoryProvider

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"local", "github", "gitlab", "gitea"})

_provider_instance: Optional[RepositoryProvider] = None

# Multi-tenant state — populated lazily alongside the provider singleton.
_multi_tenant_enabled: bool = False
_approved_orgs: frozenset[str] = frozenset()
_approved_repos: frozenset[str] = frozenset()


def get_repository_provider() -> RepositoryProvider:
    """Return the configured repository provider singleton.

    Raises:
        EnvironmentError: If ``REPO_PROVIDER`` is set to an unrecognised value,
            or if multi-tenant mode is active but no approved orgs/repos are
            configured.
    """
    global _provider_instance, _multi_tenant_enabled, _approved_orgs, _approved_repos

    if _provider_instance is not None:
        return _provider_instance

    provider_name = os.getenv("REPO_PROVIDER", "local").strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported REPO_PROVIDER value '{provider_name}'. "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    # Multi-tenant setup
    _multi_tenant_enabled = os.getenv("REPO_MULTI_TENANT", "false").strip().lower() == "true"
    if _multi_tenant_enabled:
        orgs_raw = os.getenv("APPROVED_ORGS", "").strip()
        repos_raw = os.getenv("APPROVED_REPOS", "").strip()
        if not orgs_raw and not repos_raw:
            raise EnvironmentError(
                "REPO_MULTI_TENANT=true requires at least one of APPROVED_ORGS or " "APPROVED_REPOS to be set."
            )
        _approved_orgs = frozenset(o.strip() for o in orgs_raw.split(",") if o.strip())
        _approved_repos = frozenset(r.strip() for r in repos_raw.split(",") if r.strip())

    _provider_instance = _build_provider(provider_name)
    return _provider_instance


def _build_provider(provider_name: str) -> RepositoryProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "local":
        from mcp_project_context_server.integrations.repository.local.client import (
            LocalRepositoryProvider,
        )

        return LocalRepositoryProvider()

    if provider_name == "github":
        from mcp_project_context_server.integrations.repository.github.client import (
            GitHubRepositoryProvider,
        )

        return GitHubRepositoryProvider()

    if provider_name == "gitlab":
        from mcp_project_context_server.integrations.repository.gitlab.client import (
            GitLabRepositoryProvider,
        )

        return GitLabRepositoryProvider()

    if provider_name == "gitea":
        from mcp_project_context_server.integrations.repository.gitea.client import (
            GiteaRepositoryProvider,
        )

        return GiteaRepositoryProvider()

    # Should never reach here — guarded by the caller.
    raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover


def validate_repo_access(repo_id: str) -> None:
    """Raise :exc:`RepositoryError` if *repo_id* is not in the approved allowlist.

    In single-tenant mode (``REPO_MULTI_TENANT`` unset or ``false``) this is
    always a no-op.

    Args:
        repo_id: The ``owner/repo`` (or equivalent) identifier to validate.

    Raises:
        RepositoryError: If multi-tenant mode is active and *repo_id* is not in
            the approved orgs or repos allowlists.
    """
    # Ensure the multi-tenant flags have been populated even if this is the
    # first call into the registry for this process (lazy singleton init).
    get_repository_provider()

    if not _multi_tenant_enabled:
        return

    # Check explicit repo allowlist
    if repo_id in _approved_repos:
        return

    # Check org membership — repo_id is expected to be "org/repo"
    if "/" in repo_id:
        org = repo_id.split("/", 1)[0]
        if org in _approved_orgs:
            return

    raise RepositoryError(
        f"Access to repository '{repo_id}' is not permitted. " "Check APPROVED_ORGS and APPROVED_REPOS configuration."
    )


def reset_provider_for_testing() -> None:
    """Reset the cached provider singleton and multi-tenant state.

    **For use in tests only.**  Call this in test teardown to prevent provider
    state from leaking between test cases.
    """
    global _provider_instance, _multi_tenant_enabled, _approved_orgs, _approved_repos
    _provider_instance = None
    _multi_tenant_enabled = False
    _approved_orgs = frozenset()
    _approved_repos = frozenset()
