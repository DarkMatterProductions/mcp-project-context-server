"""Tests for the HTTP/SSE transport module — auth middleware and app factory."""

import pytest
from starlette.testclient import TestClient


def _make_mock_server(mocker):
    """Build a minimal mock MCP Server."""
    mock_server = mocker.MagicMock()
    mock_server.create_initialization_options.return_value = {}
    mock_server.run = mocker.AsyncMock()
    return mock_server


class TestBearerAuth:
    def test_missing_auth_header_returns_401(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "bearer")
        monkeypatch.setenv("MCP_AUTH_TOKEN", "secret-token")

        from mcp_project_context_server.transport.sse import build_sse_app

        # Patch SseServerTransport so no real SSE logic runs
        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")
        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/sse")
        assert response.status_code == 401

    def test_wrong_token_returns_403(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "bearer")
        monkeypatch.setenv("MCP_AUTH_TOKEN", "secret-token")

        from mcp_project_context_server.transport.sse import build_sse_app

        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")
        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/sse", headers={"Authorization": "Bearer wrong-token"})
        assert response.status_code == 403

    def test_correct_token_passes_middleware(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "bearer")
        monkeypatch.setenv("MCP_AUTH_TOKEN", "secret-token")

        # Patch SseServerTransport.connect_sse so we don't need a real SSE loop
        mock_sse = mocker.MagicMock()
        mock_cm = mocker.AsyncMock()
        mock_cm.__aenter__ = mocker.AsyncMock(return_value=(mocker.MagicMock(), mocker.MagicMock()))
        mock_cm.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_sse.connect_sse.return_value = mock_cm
        mocker.patch(
            "mcp_project_context_server.transport.sse.SseServerTransport",
            return_value=mock_sse,
        )

        from mcp_project_context_server.transport.sse import build_sse_app

        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)

        # The /sse endpoint itself will "fail" because connect_sse is mocked,
        # but the auth middleware should not block it (4xx from auth would be 401/403)
        response = client.get("/sse", headers={"Authorization": "Bearer secret-token"})
        # Any status other than 401/403 means auth passed
        assert response.status_code not in (401, 403)

    def test_health_endpoint_bypasses_auth(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "bearer")
        monkeypatch.setenv("MCP_AUTH_TOKEN", "secret-token")

        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")
        from mcp_project_context_server.transport.sse import build_sse_app

        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)

        # No auth header — health should still succeed
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_missing_token_raises_at_build_time(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "bearer")
        monkeypatch.delenv("MCP_AUTH_TOKEN", raising=False)

        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")
        from mcp_project_context_server.transport.sse import build_sse_app

        with pytest.raises(EnvironmentError, match="MCP_AUTH_TOKEN must be set"):
            build_sse_app(_make_mock_server(mocker))


class TestNoAuth:
    def test_no_auth_allows_health(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "none")
        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")
        from mcp_project_context_server.transport.sse import build_sse_app

        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
        assert response.status_code == 200

    def test_unknown_auth_type_raises(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "magic")
        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")
        from mcp_project_context_server.transport.sse import build_sse_app

        with pytest.raises(EnvironmentError, match="Unsupported MCP_AUTH_TYPE"):
            build_sse_app(_make_mock_server(mocker))


class TestGoogleIAMAuth:
    def test_missing_auth_header_returns_401(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "google-iam")
        monkeypatch.delenv("GOOGLE_IAM_AUDIENCE", raising=False)
        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")
        from mcp_project_context_server.transport.sse import build_sse_app

        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/sse")
        assert response.status_code == 401

    def test_invalid_token_returns_403(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "google-iam")
        monkeypatch.delenv("GOOGLE_IAM_AUDIENCE", raising=False)
        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")

        # Patch _verify_token to raise (simulate bad token)
        mocker.patch(
            "mcp_project_context_server.transport.sse._GoogleIAMAuthMiddleware._verify_token",
            side_effect=ValueError("bad token"),
        )

        from mcp_project_context_server.transport.sse import build_sse_app

        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/sse", headers={"Authorization": "Bearer fake-id-token"})
        assert response.status_code == 403

    def test_unapproved_account_returns_403(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "google-iam")
        monkeypatch.setenv("GOOGLE_APPROVED_SERVICE_ACCOUNTS", "allowed@project.iam.gserviceaccount.com")
        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")

        mocker.patch(
            "mcp_project_context_server.transport.sse._GoogleIAMAuthMiddleware._verify_token",
            return_value={"email": "other@project.iam.gserviceaccount.com"},
        )

        from mcp_project_context_server.transport.sse import build_sse_app

        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/sse", headers={"Authorization": "Bearer fake-id-token"})
        assert response.status_code == 403

    def test_approved_account_passes(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "google-iam")
        monkeypatch.setenv("GOOGLE_APPROVED_SERVICE_ACCOUNTS", "svc@project.iam.gserviceaccount.com")
        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")

        mocker.patch(
            "mcp_project_context_server.transport.sse._GoogleIAMAuthMiddleware._verify_token",
            return_value={"email": "svc@project.iam.gserviceaccount.com"},
        )

        mock_sse = mocker.MagicMock()
        mock_cm = mocker.AsyncMock()
        mock_cm.__aenter__ = mocker.AsyncMock(return_value=(mocker.MagicMock(), mocker.MagicMock()))
        mock_cm.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_sse.connect_sse.return_value = mock_cm
        mocker.patch(
            "mcp_project_context_server.transport.sse.SseServerTransport",
            return_value=mock_sse,
        )

        from mcp_project_context_server.transport.sse import build_sse_app

        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/sse", headers={"Authorization": "Bearer valid-id-token"})
        assert response.status_code not in (401, 403)

    def test_no_approved_list_accepts_any_valid_token(self, monkeypatch, mocker):
        monkeypatch.setenv("MCP_AUTH_TYPE", "google-iam")
        monkeypatch.delenv("GOOGLE_APPROVED_SERVICE_ACCOUNTS", raising=False)
        mocker.patch("mcp_project_context_server.transport.sse.SseServerTransport")

        mocker.patch(
            "mcp_project_context_server.transport.sse._GoogleIAMAuthMiddleware._verify_token",
            return_value={"email": "anyone@example.com"},
        )

        mock_sse = mocker.MagicMock()
        mock_cm = mocker.AsyncMock()
        mock_cm.__aenter__ = mocker.AsyncMock(return_value=(mocker.MagicMock(), mocker.MagicMock()))
        mock_cm.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_sse.connect_sse.return_value = mock_cm
        mocker.patch(
            "mcp_project_context_server.transport.sse.SseServerTransport",
            return_value=mock_sse,
        )

        from mcp_project_context_server.transport.sse import build_sse_app

        app = build_sse_app(_make_mock_server(mocker))
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/sse", headers={"Authorization": "Bearer valid-id-token"})
        assert response.status_code not in (401, 403)
