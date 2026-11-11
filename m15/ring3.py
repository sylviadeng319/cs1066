# Ring 3: Multiple tools, parallel calls.

import json

import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event with attendees and optional recurrence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"},
                "attendees": {
                    "type": "array",
                    "items": {"type": "string", "format": "email"},
                },
                "recurrence": {
                    "type": "object",
                    "properties": {
                        "frequency": {"enum": ["daily", "weekly", "monthly"]},
                        "count": {"type": "integer", "minimum": 1},
                    },
                },
            },
            "required": ["title", "start", "end"],
        },
    },
    {
        "name": "list_calendar_events",
        "description": "List all calendar events on a given date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date"},
            },
            "required": ["date"],
        },
    },
]


def run_tool(name, tool_input):
    if name == "create_calendar_event":
        return {
            "event_id": "evt_123",
            "status": "created",
            "title": tool_input["title"],
        }
    if name == "list_calendar_events":
        return {
            "events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]
        }
    return {"error": f"Unknown tool: {name}"}


messages = [
    {
        "role": "user",
        "content": "Check what I have on Monday, March 30, 2026, then schedule a one-hour planning session that day that avoids any conflicts.",
    }
]

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

while response.stop_reason == "tool_use":
    # A single response can contain multiple tool_use blocks. Process all of
    # them and return all results together in one user message.
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = run_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
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


# Original code from Claude Platform Docs:
# https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent#ring-3-multiple-tools-parallel-calls
# Date copied: 20261107
#
# What to expect when you run this code:
#
# I checked your calendar for Monday, March 30 and found an existing meeting from 2pm to 3pm. I've scheduled the planning session for 10am to 11am to avoid the conflict.
