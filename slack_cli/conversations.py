"""Conversation (channel) operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def list_conversations(
    client: SlackClient,
    types: str = "public_channel,private_channel",
    exclude_archived: bool = True,
    limit: Optional[int] = None,
    as_json: bool = False,
) -> None:
    """List conversations (channels) the bot is in."""
    params = {
        "types": types,
        "exclude_archived": exclude_archived,
    }

    channels = client.paginate(
        "conversations.list",
        params=params,
        limit=limit,
        response_key="channels",
    )

    if as_json:
        print(json.dumps(channels, indent=2))
        return

    if not channels:
        print("No conversations found.")
        return

    print(f"{'ID':<15} {'Type':<10} {'Name'}")
    print("-" * 60)
    for ch in channels:
        cid = ch.get("id", "")
        name = ch.get("name", ch.get("name_normalized", ""))
        is_private = ch.get("is_private", False)
        is_im = ch.get("is_im", False)
        is_mpim = ch.get("is_mpim", False)
        if is_im:
            ctype = "DM"
        elif is_mpim:
            ctype = "Group DM"
        elif is_private:
            ctype = "Private"
        else:
            ctype = "Public"
        print(f"{cid:<15} {ctype:<10} {name}")
    print(f"\nTotal: {len(channels)} conversation(s)")


def get_info(
    client: SlackClient,
    channel: str,
    as_json: bool = False,
) -> None:
    """Get info about a conversation."""
    resp = client.call("conversations.info", params={"channel": channel})
    ch = resp.get("channel", {})

    if as_json:
        print(json.dumps(ch, indent=2))
        return

    print(f"ID:        {ch.get('id', '')}")
    print(f"Name:      {ch.get('name', '')}")
    print(f"Private:   {ch.get('is_private', False)}")
    print(f"Archived:  {ch.get('is_archived', False)}")
    print(f"Members:   {ch.get('num_members', 'N/A')}")
    topic = ch.get("topic", {}).get("value", "")
    if topic:
        print(f"Topic:     {topic}")
    purpose = ch.get("purpose", {}).get("value", "")
    if purpose:
        print(f"Purpose:   {purpose}")
    print(f"Created:   {ch.get('created', '')}")


def get_history(
    client: SlackClient,
    channel: str,
    limit: int = 100,
    oldest: Optional[str] = None,
    latest: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Get message history for a conversation."""
    params = {"channel": channel, "limit": min(limit, 1000)}
    if oldest:
        params["oldest"] = oldest
    if latest:
        params["latest"] = latest

    resp = client.call("conversations.history", params=params)
    messages = resp.get("messages", [])

    if as_json:
        print(json.dumps(messages, indent=2))
        return

    if not messages:
        print("No messages found.")
        return

    for m in messages:
        ts = m.get("ts", "")
        user = m.get("user", m.get("bot_id", "system"))
        text = m.get("text", "")[:120]
        thread = " [thread]" if m.get("thread_ts") and m.get("reply_count") else ""
        print(f"[{ts}] {user}: {text}{thread}")
    print(f"\n{len(messages)} message(s)")


def get_replies(
    client: SlackClient,
    channel: str,
    ts: str,
    limit: int = 100,
    as_json: bool = False,
) -> None:
    """Get replies in a thread."""
    params = {"channel": channel, "ts": ts, "limit": min(limit, 1000)}

    resp = client.call("conversations.replies", params=params)
    messages = resp.get("messages", [])

    if as_json:
        print(json.dumps(messages, indent=2))
        return

    if not messages:
        print("No replies found.")
        return

    for m in messages:
        msg_ts = m.get("ts", "")
        user = m.get("user", m.get("bot_id", "system"))
        text = m.get("text", "")[:120]
        parent = " (parent)" if msg_ts == ts else ""
        print(f"[{msg_ts}] {user}: {text}{parent}")
    print(f"\n{len(messages)} message(s) in thread")


def get_members(
    client: SlackClient,
    channel: str,
    limit: Optional[int] = None,
    as_json: bool = False,
) -> None:
    """Get members of a conversation."""
    members = client.paginate(
        "conversations.members",
        params={"channel": channel},
        limit=limit,
        response_key="members",
    )

    if as_json:
        print(json.dumps(members, indent=2))
        return

    if not members:
        print("No members found.")
        return

    for uid in members:
        print(f"  {uid}")
    print(f"\nTotal: {len(members)} member(s)")


def create_conversation(
    client: SlackClient,
    name: str,
    is_private: bool = False,
    as_json: bool = False,
) -> None:
    """Create a new conversation (channel)."""
    resp = client.call(
        "conversations.create",
        params={"name": name, "is_private": is_private},
    )
    ch = resp.get("channel", {})

    if as_json:
        print(json.dumps(ch, indent=2))
        return

    print(f"Created: {ch.get('id', '')} - #{ch.get('name', name)}")


def archive_conversation(
    client: SlackClient,
    channel: str,
    as_json: bool = False,
) -> None:
    """Archive a conversation."""
    resp = client.call("conversations.archive", params={"channel": channel})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Archived: {channel}")


def unarchive_conversation(
    client: SlackClient,
    channel: str,
    as_json: bool = False,
) -> None:
    """Unarchive a conversation."""
    resp = client.call("conversations.unarchive", params={"channel": channel})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Unarchived: {channel}")


def invite_to_conversation(
    client: SlackClient,
    channel: str,
    users: str,
    as_json: bool = False,
) -> None:
    """Invite users to a conversation. Users is a comma-separated list of IDs."""
    resp = client.call(
        "conversations.invite",
        params={"channel": channel, "users": users},
    )
    ch = resp.get("channel", {})

    if as_json:
        print(json.dumps(ch, indent=2))
        return

    print(f"Invited {users} to {ch.get('name', channel)}")


def kick_from_conversation(
    client: SlackClient,
    channel: str,
    user: str,
    as_json: bool = False,
) -> None:
    """Remove a user from a conversation."""
    resp = client.call(
        "conversations.kick",
        params={"channel": channel, "user": user},
    )

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Removed {user} from {channel}")


def set_topic(
    client: SlackClient,
    channel: str,
    topic: str,
    as_json: bool = False,
) -> None:
    """Set the topic for a conversation."""
    resp = client.call(
        "conversations.setTopic",
        params={"channel": channel, "topic": topic},
    )
    ch = resp.get("channel", {})

    if as_json:
        print(json.dumps(ch, indent=2))
        return

    print(f"Topic set on {ch.get('name', channel)}")


def set_purpose(
    client: SlackClient,
    channel: str,
    purpose: str,
    as_json: bool = False,
) -> None:
    """Set the purpose for a conversation."""
    resp = client.call(
        "conversations.setPurpose",
        params={"channel": channel, "purpose": purpose},
    )
    ch = resp.get("channel", {})

    if as_json:
        print(json.dumps(ch, indent=2))
        return

    print(f"Purpose set on {ch.get('name', channel)}")


def join_conversation(
    client: SlackClient,
    channel: str,
    as_json: bool = False,
) -> None:
    """Join a conversation."""
    resp = client.call("conversations.join", params={"channel": channel})
    ch = resp.get("channel", {})

    if as_json:
        print(json.dumps(ch, indent=2))
        return

    print(f"Joined: {ch.get('name', channel)}")


def leave_conversation(
    client: SlackClient,
    channel: str,
    as_json: bool = False,
) -> None:
    """Leave a conversation."""
    resp = client.call("conversations.leave", params={"channel": channel})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Left: {channel}")
