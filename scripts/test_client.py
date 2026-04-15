# test_client.py
import asyncio
import os
from pathlib import Path
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# Resolve the src/ directory so the package is importable by the subprocess
SRC_DIR = str(Path(__file__).parent.parent / "src")

async def test():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_project_context_server"],
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

asyncio.run(test())