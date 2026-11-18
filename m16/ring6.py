# Ring 6: Tools from an MCP server.
#
# Same as ring4.py, except the tool schemas and the tool function now come
# from an existing MCP server (mcp-server-time) instead of being hand-written.
# The tool-use loop is unchanged.

import asyncio
import sys

import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = anthropic.Anthropic()

# Which MCP server to start. It runs as a separate program on this machine,
# and we talk to it over MCP. Its local time zone is set to Boston's.
server = StdioServerParameters(
    command=sys.executable,
    args=["-m", "mcp_server_time", "--local-timezone=America/New_York"],
)


# The MCP library is asynchronous. Read `async` and `await` as "this step
# waits on another program" (the MCP server or Claude).
async def main():
    # Everything indented under these two lines happens while the connection
    # to the MCP server is open.
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as mcp:
            await mcp.initialize()

            # Replaces ring4.py lines 9-45: ask the server for its tool
            # schemas instead of writing them by hand.
            listed = await mcp.list_tools()
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in listed.tools
            ]

            # Replaces ring4.py lines 48-61: the server runs the tool for us.
            async def run_tool(name, tool_input):
                result = await mcp.call_tool(name, tool_input)
                text = "\n".join(
                    block.text for block in result.content if block.type == "text"
                )
                if result.is_error:
                    # The server, not our code, detected the problem.
                    raise ValueError(text)
                return text

            messages = [
                {
                    "role": "user",
                    "content": "I'm in Boston. I want to hold a one-hour planning session "
                    "on Monday, March 30, 2026 at 10am my time. What time will that be "
                    "for my teammates in Tokyo and London?",
                }
            ]

            # From here down, the same loop as ring4.py lines 72-114.
            response = client.messages.create(
                model="claude-opus-5-5",
                max_tokens=1024,
                tools=tools,
                messages=messages,
            )

            while response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        try:
                            result = await run_tool(block.name, block.input)
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    # The server already returns text, so no json.dumps().
                                    "content": result,
                                }
                            )
                        except Exception as exc:
                            # Signal failure so Claude can retry or ask for clarification.
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": str(exc),
                                    "is_error": True,
                                }
                            )

                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

                response = client.messages.create(
                    model="claude-opus-5-5",
                    max_tokens=1024,
                    tools=tools,
                    messages=messages,
                )

            final_text = next(block for block in response.content if block.type == "text")
            print(final_text.text)


asyncio.run(main())


# Derived from ../m15/ring4.py, which is from Claude Platform Docs:
# https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent#ring-4-error-handling
# Date written: 20261115
#
# MCP server: mcp-server-time, a reference server from the MCP project.
# https://github.com/modelcontextprotocol/servers/tree/main/src/time
#
# What to expect when you run this code:
#
# (Not yet run. Requires an Anthropic API key, like the other ring programs.)
