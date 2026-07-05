"""HTTP/SSE transport — general-purpose MCP over HTTP with pluggable authentication.

This transport is not tied to any specific LLM platform.  It can be used with any
MCP client that supports the HTTP/SSE protocol, including Gemini Enterprise Agent
Engine, remote Cursor deployments, and self-hosted team servers.

Configuration
-------------
``MCP_HOST``
    Bind address.  Defaults to ``0.0.0.0``.

``MCP_PORT``
    Listen port.  Defaults to ``8080``.

``MCP_AUTH_TYPE``
    Authentication type.  One of:

    ``none``
        No authentication.  Suitable for trusted internal networks.

    ``bearer``
        Static API key via ``Authorization: Bearer <token>`` header.
        Requires ``MCP_AUTH_TOKEN``.

    ``google-iam``
        Google Cloud identity token validated via ``google-auth``.
        Suitable for Gemini Enterprise Agent Engine deployments.
        Optional: ``GOOGLE_IAM_AUDIENCE``, ``GOOGLE_SERVICE_ACCOUNT_KEY_PATH``,
        ``GOOGLE_APPROVED_SERVICE_ACCOUNTS``.

``MCP_AUTH_TOKEN``
    Required when ``MCP_AUTH_TYPE=bearer``.

``GOOGLE_IAM_AUDIENCE``
    Expected ``aud`` claim in Google identity tokens.  If unset, audience
    validation is skipped (less secure — set this in production).

``GOOGLE_SERVICE_ACCOUNT_KEY_PATH``
    Path to a service account JSON key file.  If unset, Application Default
    Credentials (ADC) are used instead.

``GOOGLE_APPROVED_SERVICE_ACCOUNTS``
    Comma-separated list of allowed caller service account emails.
    If unset, any authenticated Google identity is accepted.
"""

import logging
import os
from collections.abc import Callable
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

logger = logging.getLogger(__name__)

_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 8080


# ---------------------------------------------------------------------------
# Auth middleware implementations
# ---------------------------------------------------------------------------


class _BearerAuthMiddleware(BaseHTTPMiddleware):
    """Validate ``Authorization: Bearer <token>`` against a static token."""

    def __init__(self, app: Any, token: str) -> None:
        super().__init__(app)
        self._token = token

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Health-check endpoint is unauthenticated
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Missing or invalid Authorization header"}, status_code=401)
        token = auth_header.removeprefix("Bearer ").strip()
        if token != self._token:
            return JSONResponse({"error": "Invalid bearer token"}, status_code=403)
        return await call_next(request)


class _GoogleIAMAuthMiddleware(BaseHTTPMiddleware):
    """Validate Google Cloud identity tokens (for Agent Engine and service-to-service auth)."""

    def __init__(
        self,
        app: Any,
        audience: str | None,
        approved_accounts: frozenset[str] | None,
    ) -> None:
        super().__init__(app)
        self._audience = audience
        self._approved_accounts = approved_accounts

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Missing Authorization header"}, status_code=401)

        id_token = auth_header.removeprefix("Bearer ").strip()

        try:
            import asyncio

            claims = await asyncio.to_thread(self._verify_token, id_token)
        except Exception as exc:
            logger.warning("Google IAM token verification failed: %s", exc)
            return JSONResponse({"error": f"Token verification failed: {exc}"}, status_code=403)

        if self._approved_accounts:
            email = claims.get("email", "")
            if email not in self._approved_accounts:
                logger.warning("Rejected Google identity: %s (not in approved list)", email)
                return JSONResponse({"error": "Service account not approved"}, status_code=403)

        return await call_next(request)

    def _verify_token(self, id_token: str) -> dict:
        """Verify *id_token* synchronously (called via asyncio.to_thread)."""
        try:
            from google.auth.transport import requests as google_requests  # type: ignore[import]
            from google.oauth2 import id_token as google_id_token  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "google-auth is required for google-iam auth.  "
                "Install it with: pip install mcp-project-context-server[sse]"
            ) from exc

        request = google_requests.Request()
        claims = google_id_token.verify_firebase_token(id_token, request, audience=self._audience)
        return dict(claims)


# ---------------------------------------------------------------------------
# Starlette app factory
# ---------------------------------------------------------------------------


def _build_auth_middleware(auth_type: str) -> list[Middleware]:
    """Build the Starlette middleware list for *auth_type*."""
    if auth_type == "none":
        return []

    if auth_type == "bearer":
        token = os.getenv("MCP_AUTH_TOKEN", "")
        if not token:
            raise EnvironmentError("MCP_AUTH_TOKEN must be set when MCP_AUTH_TYPE=bearer")
        return [Middleware(_BearerAuthMiddleware, token=token)]

    if auth_type == "google-iam":
        audience = os.getenv("GOOGLE_IAM_AUDIENCE") or None
        approved_raw = os.getenv("GOOGLE_APPROVED_SERVICE_ACCOUNTS", "")
        approved: frozenset[str] | None = frozenset(a.strip() for a in approved_raw.split(",") if a.strip()) or None
        return [Middleware(_GoogleIAMAuthMiddleware, audience=audience, approved_accounts=approved)]

    raise EnvironmentError(
        f"Unsupported MCP_AUTH_TYPE value '{auth_type}'.  " "Supported values are: none, bearer, google-iam"
    )


def build_sse_app(server: Server) -> Starlette:
    """Build and return the Starlette ASGI application for HTTP/SSE transport.

    :param server: (Server) The configured MCP :class:`Server` instance.
    :return: (Starlette) A :class:`~starlette.applications.Starlette` app ready
        to be served by uvicorn.
    :raises EnvironmentError: If auth configuration is invalid or incomplete.
    """
    auth_type = os.getenv("MCP_AUTH_TYPE", "none").strip().lower()
    middleware = _build_auth_middleware(auth_type)

    sse_transport = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())
        return Response()

    async def health(_: Request) -> Response:
        return JSONResponse({"status": "ok"})

    routes = [
        Route("/sse", endpoint=handle_sse),
        Route("/health", endpoint=health),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]

    return Starlette(routes=routes, middleware=middleware)


async def run_sse(server: Server) -> None:
    """Run *server* over HTTP/SSE until interrupted.

    Reads ``MCP_HOST`` and ``MCP_PORT`` from the environment.

    :param server: (Server) The configured MCP :class:`Server` instance.
    :return: (None) This function does not return a value.
    """
    import uvicorn  # type: ignore[import]

    host = os.getenv("MCP_HOST", _DEFAULT_HOST)
    port = int(os.getenv("MCP_PORT", str(_DEFAULT_PORT)))
    auth_type = os.getenv("MCP_AUTH_TYPE", "none").strip().lower()

    logger.info(
        "Starting MCP server in HTTP/SSE mode on %s:%d (auth: %s)",
        host,
        port,
        auth_type,
    )

    app = build_sse_app(server)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    uvicorn_server = uvicorn.Server(config)
    await uvicorn_server.serve()
