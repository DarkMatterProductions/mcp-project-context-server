"""Tests for the STDIO transport module."""

import pytest


class TestRunStdio:
    @pytest.mark.asyncio
    async def test_run_stdio_calls_server_run(self, mocker):
        """run_stdio should open the stdio context and call server.run."""
        mock_server = mocker.MagicMock()
        mock_server.run = mocker.AsyncMock()
        mock_server.create_initialization_options.return_value = {}

        mock_read = mocker.MagicMock()
        mock_write = mocker.MagicMock()

        mock_cm = mocker.AsyncMock()
        mock_cm.__aenter__ = mocker.AsyncMock(return_value=(mock_read, mock_write))
        mock_cm.__aexit__ = mocker.AsyncMock(return_value=None)

        mocker.patch(
            "mcp_project_context_server.transport.stdio.stdio_server",
            return_value=mock_cm,
        )

        from mcp_project_context_server.transport.stdio import run_stdio

        await run_stdio(mock_server)

        mock_server.run.assert_called_once_with(mock_read, mock_write, {})
