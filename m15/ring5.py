# Ring 5: The tool runner SDK abstraction.

import json

import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()


@beta_tool
def create_calendar_event(
    title: str,
    start: str,
    end: str,
    attendees: list[str] | None = None,
    recurrence: dict | None = None,
) -> str:
    """Create a calendar event with attendees and optional recurrence.

    Args:
        title: Event title.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
        attendees: Email addresses to invite.
        recurrence: Dict with 'frequency' (daily, weekly, monthly) and 'count'.
    """
    if attendees and len(attendees) > 10:
        raise ValueError("Too many attendees (max 10)")
    return json.dumps({"event_id": "evt_123", "status": "created", "title": title})


@beta_tool
def list_calendar_events(date: str) -> str:
    """List all calendar events on a given date.

    Args:
        date: Date in YYYY-MM-DD format.
    """
    return json.dumps(
        {"events": [{"title": "Existing meeting", "start": "14:00", "end": "15:00"}]}
    )


final_message = client.beta.messages.tool_runner(
    model="claude-opus-5-5",
    max_tokens=1024,
    tools=[create_calendar_event, list_calendar_events],
    messages=[
        {
            "role": "user",
            "content": "Check what I have on Monday, March 30, 2026, then schedule a one-hour planning session that day that avoids any conflicts.",
        }
    ],
).until_done()

for block in final_message.content:
    if block.type == "text":
        print(block.text)


# Original code from Claude Platform Docs:
# https://platform.claude.com/docs/en/agents-and-tools/tool-use/build-a-tool-using-agent#ring-5-the-tool-runner-sdk-abstraction
# Date copied: 20261107
#
# What to expect when you run this code:
#
# I checked your calendar for Monday, March 30 and found an existing meeting from 2pm to 3pm. I've scheduled the planning session for 10am to 11am to avoid the conflict.
