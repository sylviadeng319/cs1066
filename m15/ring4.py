# Ring 4: Error handling.

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
        if "attendees" in tool_input and len(tool_input["attendees"]) > 10:
            raise ValueError("Too many attendees (max 10)")
        return {
            "event_id": "evt_123",
            "status": "created",
            "title": tool_input["title"],
        }
    if name == "list_calendar_events":
        return {
            "events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]
        }
    raise ValueError(f"Unknown tool: {name}")


messages = [
    {
        "role": "user",
        "content": "Schedule a one-hour all-hands on Monday, March 30, 2026 at 10am with everyone: "
        + ", ".join(f"user{i}@example.com" for i in range(15)),
    }
]

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
                result = run_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
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


# Original code from Claude Platform Docs:
# https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent#ring-4-error-handling
# Date copied: 20261107
#
# What to expect when you run this code:
#
# I tried to schedule the all-hands but the calendar only allows 10 attendees per event. I can split this into two sessions, or you can let me know which 10 people to prioritize.
