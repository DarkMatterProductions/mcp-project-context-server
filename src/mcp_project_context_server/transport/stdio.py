"""STDIO transport — the default MCP transport for local tool clients.

No configuration required.  The server reads from stdin and writes to stdout,
which is how Claude Desktop, Claude Code, Cursor, JetBrains AI Assistant,
Continue Dev, and GitHub Copilot all launch MCP servers locally.
"""

import asyncio
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)


async def run_stdio(server: Server) -> None:
    """Run *server* over STDIO until the stream is closed.

    Args:
        server: The configured MCP :class:`Server` instance.
    """
    logger.info("Starting MCP server in STDIO mode")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
