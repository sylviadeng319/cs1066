# Ring 6 by hand: You play Claude's role.
#
# Connects to the same MCP server as ring6.py (mcp-server-time) and uses the
# same two MCP calls: list_tools() and call_tool(). But instead of Claude
# choosing which tool to call and with what inputs, you do. No Claude API
# key is needed.

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Same server as ring6.py.
server = StdioServerParameters(
    command=sys.executable,
    args=["-m", "mcp_server_time", "--local-timezone=America/New_York"],
)


async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as mcp:
            await mcp.initialize()

            # Same as ring6.py: ask the server for its tool schemas.
            listed = await mcp.list_tools()
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in listed.tools
            ]

            # This is exactly what ring6.py hands to Claude in `tools=`.
            print("The server publishes these tools:\n")
            print(json.dumps(tools, indent=2))

            while True:
                print()
                name = input("Which tool do you want to call? (Press Enter to quit) ").strip()
                if not name:
                    break
                tool = next((t for t in tools if t["name"] == name), None)
                if tool is None:
                    print(f"No tool named {name!r}.")
                    continue

                # Build the tool's input by asking for each property in its
                # schema. (Claude does this step in ring6.py.)
                schema = tool["input_schema"]
                tool_input = {}
                for prop, details in schema.get("properties", {}).items():
                    required = prop in schema.get("required", [])
                    label = "required" if required else "optional, Enter to skip"
                    print(f"  {prop}: {details.get('description', '')}")
                    value = input(f"  {prop} ({label}): ").strip()
                    if not value and not required:
                        continue
                    # The schema says whether an input is text or a whole
                    # number. If you type something that isn't a number, we
                    # send it anyway and let the server reject it.
                    if details.get("type") == "integer" and value.isdigit():
                        value = int(value)
                    tool_input[prop] = value

                print(f"\nSending to the server: {name}({json.dumps(tool_input)})")

                # Same as ring6.py: the server runs the tool.
                result = await mcp.call_tool(name, tool_input)
                text = "\n".join(
                    block.text for block in result.content if block.type == "text"
                )
                if result.is_error:
                    print("The server reported an error:")
                print(text)


asyncio.run(main())


# Written to accompany ring6.py.
# Date written: 20261115
#
# MCP server: mcp-server-time, a reference server from the MCP project.
# https://github.com/modelcontextprotocol/servers/tree/main/src/time
