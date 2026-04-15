# ADR-00001: MCP as the server protocol

## Status
Accepted

## Context

`mcp-project-context-server` needed a transport layer for exposing context tools to LLM clients. The primary targets were Claude (via Claude Code / Claude Desktop), Continue IDE, and similar AI coding assistants. The following options were considered:

- **REST API**: Standard HTTP server exposing tool endpoints. Works with any HTTP client. Requires the server to manage its own lifecycle (port binding, process supervision), authentication, and API versioning.
- **gRPC**: High-performance RPC framework with strongly-typed schemas. Not natively supported by any major AI coding assistant at the time of the decision.
- **Raw stdin/stdout (custom protocol)**: Minimal overhead. No schema, no discoverability, no standard client support.
- **MCP (Model Context Protocol) with stdio transport**: The native protocol for Claude and most AI IDE integrations. The client (Claude Code, Continue, etc.) launches the server as a subprocess and communicates over stdin/stdout using a defined JSON schema. Tool definitions are self-describing.

The server's purpose is to run alongside a developer's AI tooling on a local machine — not as a deployed service. Infrastructure overhead is undesirable.

## Decision

MCP with stdio transport was chosen as the server protocol.

The MCP framework handles tool schema declaration, JSON serialization, request routing, and lifecycle management. The stdio transport means the MCP client (Claude Code, Continue, etc.) is responsible for launching and managing the server process — eliminating the need for port management, process supervision, or authentication on the server side. Tool definitions declared in `server.py` are automatically surfaced to the LLM client as callable functions.

## Consequences

- The server is tightly coupled to the MCP ecosystem. It cannot be called from arbitrary HTTP clients without a bridge layer (e.g., an MCP-to-HTTP proxy).
- Adding new tools requires only: (1) a new handler module in `tools/`, (2) a tool definition entry in `server.py`, and (3) a dispatch entry. The MCP framework handles the rest.
- The server process is managed by the MCP client — it is started on demand and shut down with the client. No daemon or service management is required.
- Client configuration (environment variables, working directory) is passed by the MCP client's config block, which is the natural mechanism for tool configuration in this ecosystem.

## Alternatives Considered

- **REST API**: Rejected. Requires port management, lifecycle supervision, and auth — disproportionate overhead for a local single-user tool. Also not natively understood by AI IDE integrations.
- **gRPC**: Rejected. No native support in any target MCP client at the time of the decision.
- **Raw stdin/stdout**: Rejected. No schema, no discoverability, no standard client library support. Would require reimplementing what MCP provides.
