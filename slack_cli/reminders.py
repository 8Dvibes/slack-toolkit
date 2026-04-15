"""Reminder operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def add_reminder(
    client: SlackClient,
    text: str,
    time: str,
    user: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Create a reminder.

    time: Unix timestamp, natural language string (e.g. 'in 30 minutes'), or
          ISO 8601 string.
    """
    params = {"text": text, "time": time}
    if user:
        params["user"] = user

    resp = client.call("reminders.add", params=params)
    reminder = resp.get("reminder", {})

    if as_json:
        print(json.dumps(reminder, indent=2))
        return

    rid = reminder.get("id", "")
    rtime = reminder.get("time", "")
    ruser = reminder.get("user", user or "me")
    print(f"Reminder created: {rid}")
    print(f"  Text: {text}")
    print(f"  For:  {ruser}")
    print(f"  At:   {rtime}")


def list_reminders(
    client: SlackClient,
    as_json: bool = False,
) -> None:
    """List reminders for the authed user."""
    resp = client.call("reminders.list")
    reminders = resp.get("reminders", [])

    if as_json:
        print(json.dumps(reminders, indent=2))
        return

    if not reminders:
        print("No reminders found.")
        return

    print(f"{'ID':<15} {'Complete':<10} {'Text'}")
    print("-" * 70)
    for r in reminders:
        rid = r.get("id", "")
        complete = "yes" if r.get("complete_ts") else "no"
        text = r.get("text", "")[:50]
        print(f"{rid:<15} {complete:<10} {text}")
    print(f"\nTotal: {len(reminders)} reminder(s)")


def complete_reminder(
    client: SlackClient,
    reminder: str,
    as_json: bool = False,
) -> None:
    """Mark a reminder as complete."""
    resp = client.call("reminders.complete", params={"reminder": reminder})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Reminder {reminder} marked complete.")


def delete_reminder(
    client: SlackClient,
    reminder: str,
    as_json: bool = False,
) -> None:
    """Delete a reminder."""
    resp = client.call("reminders.delete", params={"reminder": reminder})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Reminder {reminder} deleted.")


def get_reminder_info(
    client: SlackClient,
    reminder: str,
    as_json: bool = False,
) -> None:
    """Get info about a specific reminder."""
    resp = client.call("reminders.info", params={"reminder": reminder})
    r = resp.get("reminder", {})

    if as_json:
        print(json.dumps(r, indent=2))
        return

    print(f"ID:        {r.get('id', '')}")
    print(f"Text:      {r.get('text', '')}")
    print(f"User:      {r.get('user', '')}")
    print(f"Time:      {r.get('time', '')}")
    print(f"Complete:  {'yes' if r.get('complete_ts') else 'no'}")
    if r.get("recurring"):
        print(f"Recurring: yes")
