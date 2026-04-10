"""Chat message operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def post_message(
    client: SlackClient,
    channel: str,
    text: str,
    blocks: Optional[str] = None,
    thread_ts: Optional[str] = None,
    unfurl_links: bool = True,
    as_json: bool = False,
) -> None:
    """Post a message to a channel."""
    params = {
        "channel": channel,
        "text": text,
        "unfurl_links": unfurl_links,
    }
    if blocks:
        params["blocks"] = json.loads(blocks) if isinstance(blocks, str) else blocks
    if thread_ts:
        params["thread_ts"] = thread_ts

    resp = client.call("chat.postMessage", params=params)

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    ts = resp.get("ts", "")
    ch = resp.get("channel", channel)
    print(f"Message posted to {ch} (ts: {ts})")


def update_message(
    client: SlackClient,
    channel: str,
    ts: str,
    text: Optional[str] = None,
    blocks: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Update an existing message."""
    params = {"channel": channel, "ts": ts}
    if text is not None:
        params["text"] = text
    if blocks:
        params["blocks"] = json.loads(blocks) if isinstance(blocks, str) else blocks

    resp = client.call("chat.update", params=params)

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Message updated (ts: {resp.get('ts', ts)})")


def delete_message(
    client: SlackClient,
    channel: str,
    ts: str,
    as_json: bool = False,
) -> None:
    """Delete a message."""
    resp = client.call("chat.delete", params={"channel": channel, "ts": ts})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Message deleted (ts: {ts})")


def schedule_message(
    client: SlackClient,
    channel: str,
    text: str,
    post_at: int,
    blocks: Optional[str] = None,
    thread_ts: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Schedule a message for future delivery."""
    params = {
        "channel": channel,
        "text": text,
        "post_at": post_at,
    }
    if blocks:
        params["blocks"] = json.loads(blocks) if isinstance(blocks, str) else blocks
    if thread_ts:
        params["thread_ts"] = thread_ts

    resp = client.call("chat.scheduleMessage", params=params)

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    sid = resp.get("scheduled_message_id", "")
    print(f"Message scheduled (id: {sid}, post_at: {post_at})")


def delete_scheduled_message(
    client: SlackClient,
    channel: str,
    scheduled_message_id: str,
    as_json: bool = False,
) -> None:
    """Delete a scheduled message before it sends."""
    resp = client.call(
        "chat.deleteScheduledMessage",
        params={"channel": channel, "scheduled_message_id": scheduled_message_id},
    )

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Scheduled message deleted (id: {scheduled_message_id})")


def list_scheduled_messages(
    client: SlackClient,
    channel: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """List scheduled messages."""
    params = {}
    if channel:
        params["channel"] = channel

    resp = client.call("chat.scheduledMessages.list", params=params)
    messages = resp.get("scheduled_messages", [])

    if as_json:
        print(json.dumps(messages, indent=2))
        return

    if not messages:
        print("No scheduled messages.")
        return

    print(f"{'ID':<30} {'Channel':<15} {'Post At':<15} {'Text'}")
    print("-" * 80)
    for m in messages:
        mid = m.get("id", "")
        ch = m.get("channel_id", "")
        post_at = m.get("post_at", "")
        text = m.get("text", "")[:40]
        print(f"{mid:<30} {ch:<15} {post_at:<15} {text}")
    print(f"\nTotal: {len(messages)} scheduled message(s)")


def get_permalink(
    client: SlackClient,
    channel: str,
    message_ts: str,
    as_json: bool = False,
) -> None:
    """Get a permalink for a message."""
    resp = client.call(
        "chat.getPermalink",
        params={"channel": channel, "message_ts": message_ts},
    )

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(resp.get("permalink", ""))
