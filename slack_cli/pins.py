"""Pin operations for slack-cli."""

import json
import sys

from .client import SlackClient


def add_pin(
    client: SlackClient,
    channel: str,
    timestamp: str,
    as_json: bool = False,
) -> None:
    """Pin a message to a channel."""
    resp = client.call(
        "pins.add",
        params={"channel": channel, "timestamp": timestamp},
    )

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Pinned message {timestamp} in {channel}")


def remove_pin(
    client: SlackClient,
    channel: str,
    timestamp: str,
    as_json: bool = False,
) -> None:
    """Unpin a message from a channel."""
    resp = client.call(
        "pins.remove",
        params={"channel": channel, "timestamp": timestamp},
    )

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Unpinned message {timestamp} from {channel}")


def list_pins(
    client: SlackClient,
    channel: str,
    as_json: bool = False,
) -> None:
    """List pinned items in a channel."""
    resp = client.call("pins.list", params={"channel": channel})
    items = resp.get("items", [])

    if as_json:
        print(json.dumps(items, indent=2))
        return

    if not items:
        print(f"No pinned items in {channel}.")
        return

    for item in items:
        itype = item.get("type", "message")
        if itype == "message":
            msg = item.get("message", {})
            ts = msg.get("ts", "")
            user = msg.get("user", "")
            text = msg.get("text", "")[:80]
            print(f"  [{ts}] @{user}: {text}")
        elif itype == "file":
            f = item.get("file", {})
            print(f"  File: {f.get('name', '')} ({f.get('id', '')})")
    print(f"\nTotal: {len(items)} pinned item(s)")
