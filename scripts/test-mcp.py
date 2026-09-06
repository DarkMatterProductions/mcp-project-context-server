import argparse
import asyncio
import json
import os
import sys
from typing import Dict

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
TEST_PAYLOADS = {}

# ==========================================
# ARGUMENTS
# ==========================================

parser = argparse.ArgumentParser(description="Script for rendering output from the MCP server")
parser.add_argument("--tool", "-t", choices=list(TEST_PAYLOADS.keys()).append("all"), default="all")
parser.add_argument("--gh-org", "-o", type=str)
parser.add_argument("--details", "-d", action="store_true")
args = parser.parse_args()

TEST_PAYLOADS = {
    "search_context_index": {
        "name": "search_context_index",
        "arguments": {
            "project_path": TEST_PATH,
            "query": "architecture notes",
            "n_results": 2
        }
    },
    "search_adr_index": {
        "name": "search_adr_index",
        "arguments": {
            "project_path": TEST_PATH,
            "query": "architecture decisions",
            "n_results": 2
        }
    },
    "search_session_files": {
        "name": "search_session_files",
        "arguments": {
            "project_path": TEST_PATH,
            "query": "session summary",
            "n_results": 2
        }
    },
    "find_latest_session_file": {
        "name": "find_latest_session_file",
        "arguments": {"project_path": TEST_PATH}
    },
    "load_context_files": {
        "name": "load_context_files",
        "arguments": {"project_path": TEST_PATH, "files": ["project.md"]}
    },
    "reload_active_context_file": {
        "name": "reload_active_context_file",
        "arguments": {
            "project_path": TEST_PATH,
            "files": [{"path": "project.md", "known_sha512": "deadbeef"}]
        }
    },
    "save_session_summary": {
        "name": "save_session_summary",
        "arguments": {
            "project_path": TEST_PATH,
            "summary": "### Session\n- Upgraded script to handle massive JSON streams."
        }
    },
    "index_project_context": {
        "name": "index_project_context",
        "arguments": {"project_path": TEST_PATH}
    }
}

if args.gh_org:
    print(f"Listing repositories for organization: {args.gh_org}")
    TEST_PAYLOADS["list_repositories"] = {
        "name": "list_repositories",
        "arguments": {"org": f"{args.gh_org}"}
    }

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
    print(f"\n[CLIENT -> SERVER] Request Sent\n"
          f"    ID: {request_id}\n"
          f"    method: {method}\n"
          f"    params: {params}\n"
          )

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

from typing import Any

def trunc_json_values(value: Any, details: bool, level: int = 0) -> Any:
    if isinstance(value, str):
        if len(value) > 1000 and not details:
            return f"{value[:200]} ... [TRUNCATED FOR TERMINAL READABILITY] ..."
        return value

    if isinstance(value, dict):
        return {
            key: trunc_json_values(item, details, level + 1)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            trunc_json_values(item, details, level + 1)
            for item in value
        ]

    return value

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
        payloads: Dict[str, str | Dict[str, str | Dict[str, str | int]]] = TEST_PAYLOADS if args.tool == "all" else {args.tool: TEST_PAYLOADS[args.tool]}
        for tool_name, tool in payloads.items():
            req_id += 1
            print(f"[SERVER -> CLIENT] Request for '{tool_name}':")
            tool_request = json.dumps(tool, indent=2)
            print(tool_request)

            await send_request(writer, "tools/call", tool, req_id)

            response = await read_response(reader)
            print(f"[SERVER -> CLIENT] Response for '{tool_name}':")

            if isinstance(response, dict):
                resp_str = json.dumps({key: trunc_json_values(value, args.details) for key, value in response.items()}, indent=2)
            else:
                print("No response.")
                break

            print(resp_str)
            print(f"Total Response Length: {len(resp_str)} characters.")
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
