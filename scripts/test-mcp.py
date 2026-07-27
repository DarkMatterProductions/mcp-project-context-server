import asyncio
import json
import os
import sys

# ==========================================
# CONFIGURATION
# ==========================================
# sys.executable automatically tracks the active virtualenv's Python binary
SERVER_COMMAND = [sys.executable, "-m", "mcp_project_context_server.__main__"]

# Set a massive buffer size (32 Megabytes) to handle giant project file contexts
STREAM_BUFFER_LIMIT = 32 * 1024 * 1024

# A real path on your system to bypass validation checks
TEST_PATH = r"C:/Users/drahk/DMPProjects/mcp-project-context-server"

# ==========================================
# TEST PAYLOADS
# ==========================================
TEST_PAYLOADS = [
    {
        "name": "load_project_context",
        "arguments": {"project_path": TEST_PATH}
    },
    {
        "name": "search_project_context",
        "arguments": {
            "project_path": TEST_PATH,
            "query": "architecture notes",
            "n_results": 2
        }
    },
    {
        "name": "save_session_summary",
        "arguments": {
            "project_path": TEST_PATH,
            "summary": "### Session\n- Upgraded script to handle massive JSON streams."
        }
    },
    {
        "name": "index_project_context",
        "arguments": {"project_path": TEST_PATH}
    },
    {
        "name": "list_repositories",
        "arguments": {"org": "my-org"}
    }
]

async def read_response(reader):
    """Reads a single line/message from the server stdout safely on Windows."""
    try:
        line = await reader.readline()
        if not line:
            return None
        cleaned_line = line.decode('utf-8').strip()
        return json.loads(cleaned_line)
    except asyncio.LimitOverrunError as e:
        print(f"\n[CRITICAL ERROR]: Line exceeded the stream buffer! {e}")
        raise

async def send_request(writer, method, params, request_id):
    """Formats and sends a JSON-RPC request to the server."""
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params
    }
    raw_payload = json.dumps(payload) + "\n"
    writer.write(raw_payload.encode('utf-8'))
    await writer.drain()
    print(f"\n[CLIENT -> SERVER] Sent method: {method} (ID: {request_id})")

async def send_notification(writer, method, params):
    """Sends a JSON-RPC notification (no ID, no response expected)."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params
    }
    raw_payload = json.dumps(payload) + "\n"
    writer.write(raw_payload.encode('utf-8'))
    await writer.drain()
    print(f"[CLIENT -> SERVER] Sent notification: {method}")

async def main():
    print(f"Starting MCP server via: {' '.join(SERVER_COMMAND)}")
    print(f"Applying StreamReader stream limit: {STREAM_BUFFER_LIMIT // (1024*1024)} MB")

    # CRITICAL FIX: Pass 'limit' argument directly to the executive wrapper
    process = await asyncio.create_subprocess_exec(
        *SERVER_COMMAND,
        env=os.environ,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=None,                  # Pushes raw execution exceptions directly to your screen
        limit=STREAM_BUFFER_LIMIT      # Overrides the default 64KB lock with 32MB
    )

    writer = process.stdin
    reader = process.stdout
    req_id = 1

    try:
        # Handshake Phase 1
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-test-harness", "version": "1.0.0"}
        }
        await send_request(writer, "initialize", init_params, req_id)

        init_resp = await read_response(reader)
        print(f"[SERVER -> CLIENT] Init Response received.")

        # Handshake Phase 2
        req_id += 1
        await send_notification(writer, "notifications/initialized", {})
        print("Handshake completed successfully!\n" + "="*50)

        # Loop and test every single schema definition
        for tool in TEST_PAYLOADS:
            req_id += 1
            tool_name = tool["name"]

            await send_request(writer, "tools/call", tool, req_id)

            response = await read_response(reader)
            print(f"[SERVER -> CLIENT] Response for '{tool_name}':")

            # Print response preview cleanly (truncates giant text so terminal doesn't lag)
            resp_str = json.dumps(response, indent=2)
            if len(resp_str) > 1000:
                # print(resp_str[:1000] + "\n\n... [TRUNCATED FOR TERMINAL READABILITY] ...")
                print(resp_str)
                print(f"Total Response Length: {len(resp_str)} characters.")
            else:
                print(resp_str)
            print("-" * 50)

    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        print("Closing server connection...")
        writer.close()
        await writer.wait_closed()
        process.terminate()
        await process.wait()
        print("Server process stopped.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
