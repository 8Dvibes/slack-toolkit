"""Reaction operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def add_reaction(
    client: SlackClient,
    channel: str,
    timestamp: str,
    name: str,
    as_json: bool = False,
) -> None:
    """Add a reaction to a message."""
    resp = client.call(
        "reactions.add",
        params={"channel": channel, "timestamp": timestamp, "name": name},
    )

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Added :{name}: to message {timestamp}")


def remove_reaction(
    client: SlackClient,
    channel: str,
    timestamp: str,
    name: str,
    as_json: bool = False,
) -> None:
    """Remove a reaction from a message."""
    resp = client.call(
        "reactions.remove",
        params={"channel": channel, "timestamp": timestamp, "name": name},
    )

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Removed :{name}: from message {timestamp}")


def get_reactions(
    client: SlackClient,
    channel: str,
    timestamp: str,
    as_json: bool = False,
) -> None:
    """Get reactions on a message."""
    resp = client.call(
        "reactions.get",
        params={"channel": channel, "timestamp": timestamp, "full": True},
    )
    message = resp.get("message", {})
    reactions = message.get("reactions", [])

    if as_json:
        print(json.dumps(reactions, indent=2))
        return

    if not reactions:
        print("No reactions on this message.")
        return

    for r in reactions:
        name = r.get("name", "")
        count = r.get("count", 0)
        users = r.get("users", [])
        user_str = ", ".join(users[:5])
        if len(users) > 5:
            user_str += f" +{len(users) - 5} more"
        print(f"  :{name}: ({count}) - {user_str}")


def list_reactions(
    client: SlackClient,
    user: Optional[str] = None,
    count: int = 100,
    as_json: bool = False,
) -> None:
    """List reactions made by a user."""
    params = {"count": count, "full": True}
    if user:
        params["user"] = user

    resp = client.call("reactions.list", params=params)
    items = resp.get("items", [])

    if as_json:
        print(json.dumps(items, indent=2))
        return

    if not items:
        print("No reactions found.")
        return

    for item in items:
        itype = item.get("type", "message")
        if itype == "message":
            msg = item.get("message", {})
            text = msg.get("text", "")[:80]
            reactions = msg.get("reactions", [])
            reaction_str = " ".join(f":{r['name']}:" for r in reactions)
            print(f"  {text}")
            print(f"    {reaction_str}")
        elif itype == "file":
            f = item.get("file", {})
            print(f"  File: {f.get('name', '')} ({f.get('id', '')})")
    print(f"\nTotal: {len(items)} item(s) with reactions")
