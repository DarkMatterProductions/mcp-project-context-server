"""Tests for the resolve_project_path helper in helpers/context.py."""

from mcp_project_context_server.helpers.context import collection_name_for_repo_id, resolve_project_path


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


class TestCollectionNameForRepoId:
    """Tests for the collection_name_for_repo_id helper function."""

    def test_short_identifier(self):
        assert collection_name_for_repo_id("owner/repo") == "ctx_owner_repo"

    def test_normalises_full_url(self):
        assert collection_name_for_repo_id("https://github.com/owner/repo") == "ctx_owner_repo"

    def test_same_name_different_owner_does_not_collide(self):
        a = collection_name_for_repo_id("acme/backend")
        b = collection_name_for_repo_id("other-org/backend")
        assert a != b

    def test_hyphens_and_spaces_are_sanitized(self):
        result = collection_name_for_repo_id("my-org/my repo")
        assert "-" not in result
        assert " " not in result

    def test_truncated_to_63_chars(self):
        long_repo = "a" * 40 + "/" + "b" * 40
        result = collection_name_for_repo_id(long_repo)
        assert len(result) <= 63
