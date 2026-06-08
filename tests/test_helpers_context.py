"""Tests for the resolve_project_path helper in helpers/context.py."""
import pytest

from mcp_project_context_server.helpers.context import resolve_project_path


class TestResolveProjectPath:
    """Tests for the resolve_project_path helper function."""

    def test_http_url_is_remote(self):
        path, is_remote = resolve_project_path("http://github.com/owner/repo")
        assert is_remote is True
        assert path == "http://github.com/owner/repo"

    def test_https_url_is_remote(self):
        path, is_remote = resolve_project_path("https://github.com/owner/repo")
        assert is_remote is True
        assert path == "https://github.com/owner/repo"

    def test_short_identifier_is_remote(self):
        path, is_remote = resolve_project_path("owner/repo")
        assert is_remote is True
        assert path == "owner/repo"

    def test_short_identifier_with_dots_is_remote(self):
        path, is_remote = resolve_project_path("my-org/my.repo")
        assert is_remote is True
        assert path == "my-org/my.repo"

    def test_filesystem_path_is_not_remote(self):
        path, is_remote = resolve_project_path("/home/user/projects/myapp")
        assert is_remote is False
        assert path == "/home/user/projects/myapp"

    def test_path_with_subdirs_is_not_remote(self):
        path, is_remote = resolve_project_path("/home/user/projects/myapp/src")
        assert is_remote is False
        assert path == "/home/user/projects/myapp/src"

    def test_relative_path_with_multiple_components_is_not_remote(self):
        path, is_remote = resolve_project_path("some/longer/path")
        assert is_remote is False
        assert path == "some/longer/path"

    def test_plain_directory_name_is_not_remote(self):
        path, is_remote = resolve_project_path("myproject")
        assert is_remote is False
        assert path == "myproject"
