"""Search operations for slack-cli.

IMPORTANT: All search.* methods require a user token (xoxp-), not a bot token.
"""

import json
import sys
from typing import Optional

from .client import SlackClient


def search_messages(
    client: SlackClient,
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
    as_json: bool = False,
) -> None:
    """Search for messages matching a query. Requires user token."""
    params = {
        "query": query,
        "sort": sort,
        "sort_dir": sort_dir,
        "count": count,
    }

    resp = client.call("search.messages", params=params, token_type="user")
    messages = resp.get("messages", {})
    matches = messages.get("matches", [])

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    if not matches:
        print(f"No messages found for: {query}")
        return

    total = messages.get("total", len(matches))
    print(f"Found {total} message(s) for: {query}\n")

    for m in matches:
        ts = m.get("ts", "")
        user = m.get("username", m.get("user", ""))
        ch = m.get("channel", {})
        ch_name = ch.get("name", "") if isinstance(ch, dict) else str(ch)
        text = m.get("text", "")[:120]
        print(f"[{ts}] #{ch_name} @{user}: {text}")
    print(f"\nShowing {len(matches)} of {total}")


def search_files(
    client: SlackClient,
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
    as_json: bool = False,
) -> None:
    """Search for files matching a query. Requires user token."""
    params = {
        "query": query,
        "sort": sort,
        "sort_dir": sort_dir,
        "count": count,
    }

    resp = client.call("search.files", params=params, token_type="user")
    files = resp.get("files", {})
    matches = files.get("matches", [])

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    if not matches:
        print(f"No files found for: {query}")
        return

    total = files.get("total", len(matches))
    print(f"Found {total} file(s) for: {query}\n")

    for f in matches:
        fid = f.get("id", "")
        name = f.get("name", "untitled")
        ftype = f.get("filetype", "")
        user = f.get("user", "")
        print(f"  {fid}  {name} ({ftype}) by {user}")
    print(f"\nShowing {len(matches)} of {total}")


def search_all(
    client: SlackClient,
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
    as_json: bool = False,
) -> None:
    """Search for messages and files matching a query. Requires user token."""
    params = {
        "query": query,
        "sort": sort,
        "sort_dir": sort_dir,
        "count": count,
    }

    resp = client.call("search.all", params=params, token_type="user")

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    # Messages
    messages = resp.get("messages", {})
    msg_matches = messages.get("matches", [])
    msg_total = messages.get("total", 0)

    # Files
    files = resp.get("files", {})
    file_matches = files.get("matches", [])
    file_total = files.get("total", 0)

    print(f"Search: {query}")
    print(f"Messages: {msg_total}, Files: {file_total}\n")

    if msg_matches:
        print("--- Messages ---")
        for m in msg_matches[:10]:
            ts = m.get("ts", "")
            user = m.get("username", m.get("user", ""))
            text = m.get("text", "")[:100]
            print(f"  [{ts}] @{user}: {text}")

    if file_matches:
        print("\n--- Files ---")
        for f in file_matches[:10]:
            fid = f.get("id", "")
            name = f.get("name", "untitled")
            print(f"  {fid}  {name}")
