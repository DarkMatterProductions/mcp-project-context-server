# test_client.py
import asyncio
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

async def test():
    async with stdio_client(["python", "project_context_server/server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

asyncio.run(test())