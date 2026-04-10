"""Bookmark operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def add_bookmark(
    client: SlackClient,
    channel: str,
    title: str,
    link: str,
    type: str = "link",
    emoji: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Add a bookmark to a channel."""
    params = {
        "channel_id": channel,
        "title": title,
        "type": type,
        "link": link,
    }
    if emoji:
        params["emoji"] = emoji

    resp = client.call("bookmarks.add", params=params)
    bm = resp.get("bookmark", {})

    if as_json:
        print(json.dumps(bm, indent=2))
        return

    print(f"Added bookmark: {bm.get('id', '')} - {bm.get('title', title)}")


def edit_bookmark(
    client: SlackClient,
    channel: str,
    bookmark_id: str,
    title: Optional[str] = None,
    link: Optional[str] = None,
    emoji: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Edit a bookmark."""
    params = {
        "channel_id": channel,
        "bookmark_id": bookmark_id,
    }
    if title is not None:
        params["title"] = title
    if link is not None:
        params["link"] = link
    if emoji is not None:
        params["emoji"] = emoji

    resp = client.call("bookmarks.edit", params=params)
    bm = resp.get("bookmark", {})

    if as_json:
        print(json.dumps(bm, indent=2))
        return

    print(f"Updated bookmark: {bm.get('id', bookmark_id)}")


def list_bookmarks(
    client: SlackClient,
    channel: str,
    as_json: bool = False,
) -> None:
    """List bookmarks in a channel."""
    resp = client.call("bookmarks.list", params={"channel_id": channel})
    bookmarks = resp.get("bookmarks", [])

    if as_json:
        print(json.dumps(bookmarks, indent=2))
        return

    if not bookmarks:
        print(f"No bookmarks in {channel}.")
        return

    for bm in bookmarks:
        bid = bm.get("id", "")
        title = bm.get("title", "")
        link = bm.get("link", "")
        emoji = bm.get("emoji", "")
        prefix = f"{emoji} " if emoji else ""
        print(f"  {bid}  {prefix}{title}")
        if link:
            print(f"         {link}")
    print(f"\nTotal: {len(bookmarks)} bookmark(s)")


def remove_bookmark(
    client: SlackClient,
    channel: str,
    bookmark_id: str,
    as_json: bool = False,
) -> None:
    """Remove a bookmark from a channel."""
    resp = client.call(
        "bookmarks.remove",
        params={"channel_id": channel, "bookmark_id": bookmark_id},
    )

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Removed bookmark: {bookmark_id}")
