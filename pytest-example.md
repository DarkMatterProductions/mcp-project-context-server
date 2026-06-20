# MCP Server Integration Testing with Python

Integration testing an MCP server means writing tests that actually speak the MCP protocol
over stdio — booting your real server process and exercising it end-to-end. This sits between
unit tests (pure Python, no protocol) and manual testing in Claude Desktop.

---

## Prerequisites

```bash
pip install mcp pytest pytest-asyncio
```

Your `pytest.ini` (or `pyproject.toml`) should enable async mode:

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

---

## Core Pattern

Every integration test follows the same structure:

1. Define `StdioServerParameters` pointing at your server process
2. Open a `stdio_client` context — this spawns the process
3. Open a `ClientSession` context — this handles the MCP handshake
4. Call `session.initialize()`
5. Make assertions

```python
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
def server_params():
    return StdioServerParameters(
        command="python",
        args=["my_server.py"],
        # Optional: pass env vars to the server process
        env={"MY_API_KEY": "test-key"}
    )


async def test_example(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # your assertions here
```

---

## Testing Tools

### List available tools

```python
async def test_tools_are_registered(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_tools()
            tool_names = [t.name for t in result.tools]

            assert "get_weather" in tool_names
            assert "search_docs" in tool_names
```

### Call a tool and inspect output

```python
async def test_get_weather_returns_city(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("get_weather", {"city": "Chicago"})

            # result.content is a list of content blocks
            assert len(result.content) > 0
            assert result.content[0].type == "text"
            assert "Chicago" in result.content[0].text
```

### Test tool error handling

```python
async def test_missing_argument_raises_error(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("get_weather", {})  # missing 'city'

            # MCP surfaces errors as isError=True, not exceptions
            assert result.isError is True
```

---

## Testing Resources

### List available resources

```python
async def test_resources_are_registered(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_resources()
            uris = [r.uri for r in result.resources]

            assert "file:///config" in uris
```

### Read a resource

```python
async def test_read_config_resource(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.read_resource("file:///config")

            assert len(result.contents) > 0
            # Text resources have a .text attribute
            assert "version" in result.contents[0].text
```

---

## Testing Prompts

### List available prompts

```python
async def test_prompts_are_registered(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_prompts()
            prompt_names = [p.name for p in result.prompts]

            assert "summarise" in prompt_names
```

### Get a prompt with arguments

```python
async def test_summarise_prompt(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.get_prompt(
                "summarise",
                {"text": "The quick brown fox jumps over the lazy dog."}
            )

            # result.messages is a list of PromptMessage objects
            assert len(result.messages) > 0
            assert result.messages[0].role == "user"
```

---

## Shared Fixture (DRY)

If you have many tests, avoid repeating the context manager boilerplate with a session fixture:

```python
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
def server_params():
    return StdioServerParameters(command="python", args=["my_server.py"])


@pytest.fixture
async def session(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            yield s  # tests run here; both contexts stay open


# Tests now just receive `session` directly
async def test_tools(session):
    result = await session.list_tools()
    assert len(result.tools) > 0


async def test_weather(session):
    result = await session.call_tool("get_weather", {"city": "Chicago"})
    assert "Chicago" in result.content[0].text
```

> **Note:** Each test gets a **fresh server process** because the fixture spins up a new
> `stdio_client` per test. If startup is slow, scope the fixture to `"module"` or `"session"`,
> but be aware that state may bleed between tests.

---

## Running the Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run a single test
pytest tests/integration/test_tools.py::test_get_weather_returns_city -v

# Run with stdout visible (useful when debugging server logs)
pytest tests/integration/ -v -s
```

---

## Tips

- **Keep unit tests separate** — integration tests are slower because they spawn a real process.
  Put them in a dedicated `tests/integration/` directory and run them separately in CI.

- **Server logs go to stderr** — MCP servers write logs to stderr so they don't interfere with
  the stdio transport. Use `-s` with pytest to see them, or redirect: `args=["my_server.py"],
  env={"LOG_LEVEL": "DEBUG"}`.

- **`result.isError` vs exceptions** — the MCP client does not raise Python exceptions for
  tool errors. Instead, `result.isError` is `True` and the error message is in
  `result.content[0].text`. Always check `isError` when testing failure paths.

- **`initialize()` is mandatory** — skipping it will cause all subsequent calls to hang or fail.
  Always call it right after opening the session.