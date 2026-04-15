"""Conversation (channel) operations for slack-cli."""

import csv
import io
import json
import random
import sys
import time
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


def open_dm(
    client: SlackClient,
    users: str,
    as_json: bool = False,
) -> None:
    """Open a DM or group DM. If emails given, resolve via users.lookupByEmail first."""
    user_ids = []
    for u in users.split(","):
        u = u.strip()
        if not u:
            continue
        if "@" in u:
            # Resolve email to user ID
            resp = client.call("users.lookupByEmail", params={"email": u})
            uid = resp.get("user", {}).get("id", "")
            if not uid:
                print(f"Warning: Could not resolve {u}", file=sys.stderr)
                continue
            user_ids.append(uid)
        else:
            user_ids.append(u)

    if not user_ids:
        print("Error: No valid users specified.", file=sys.stderr)
        sys.exit(1)

    resp = client.call(
        "conversations.open",
        params={"users": ",".join(user_ids)},
    )
    ch = resp.get("channel", {})

    if as_json:
        print(json.dumps(ch, indent=2))
        return

    ch_id = ch.get("id", "")
    is_im = ch.get("is_im", False)
    ch_type = "DM" if is_im else "Group DM"
    print(f"Opened {ch_type}: {ch_id}")
    print(f"  Users: {', '.join(user_ids)}")


def invite_all_to_conversation(
    client: SlackClient,
    channel: str,
    dry_run: bool = False,
    as_json: bool = False,
) -> None:
    """Invite ALL workspace members to a channel."""
    # Get current members
    current_members = set(
        client.paginate("conversations.members", params={"channel": channel}, response_key="members")
    )
    # Get all users
    all_users = client.paginate("users.list", response_key="members")
    # Filter: only real, non-deleted, non-bot users not already in channel
    to_invite = []
    for user in all_users:
        if user.get("deleted") or user.get("is_bot") or user.get("id") == "USLACKBOT":
            continue
        uid = user.get("id", "")
        if uid and uid not in current_members:
            to_invite.append(uid)

    if as_json:
        result = {
            "channel": channel,
            "to_invite": to_invite,
            "already_member": len(current_members),
            "dry_run": dry_run,
        }
        print(json.dumps(result, indent=2))
        return

    print(f"Channel: {channel}")
    print(f"Already members: {len(current_members)}")
    print(f"To invite: {len(to_invite)}")

    if dry_run:
        print("\n[DRY RUN] Would invite:")
        for uid in to_invite:
            print(f"  {uid}")
        return

    if not to_invite:
        print("All users are already members.")
        return

    # Invite in batches of 30 (Slack limit)
    invited = 0
    errors = 0
    batch_size = 30
    for i in range(0, len(to_invite), batch_size):
        batch = to_invite[i:i + batch_size]
        try:
            client.call(
                "conversations.invite",
                params={"channel": channel, "users": ",".join(batch)},
            )
            invited += len(batch)
            print(f"  Invited batch {i // batch_size + 1}: {len(batch)} users")
        except Exception as e:
            errors += len(batch)
            print(f"  Error on batch: {e}", file=sys.stderr)

    print(f"\nDone. Invited: {invited}, Errors: {errors}")


def clone_members(
    client: SlackClient,
    from_channel: str,
    to_channel: str,
    dry_run: bool = False,
    as_json: bool = False,
) -> None:
    """Copy all members from one channel to another."""
    from_members = set(
        client.paginate("conversations.members", params={"channel": from_channel}, response_key="members")
    )
    to_members = set(
        client.paginate("conversations.members", params={"channel": to_channel}, response_key="members")
    )

    to_invite = list(from_members - to_members)

    if as_json:
        result = {
            "from_channel": from_channel,
            "to_channel": to_channel,
            "from_member_count": len(from_members),
            "to_member_count": len(to_members),
            "to_invite": to_invite,
            "dry_run": dry_run,
        }
        print(json.dumps(result, indent=2))
        return

    print(f"From: {from_channel} ({len(from_members)} members)")
    print(f"To:   {to_channel} ({len(to_members)} members)")
    print(f"To invite: {len(to_invite)}")

    if dry_run:
        print("\n[DRY RUN] Would invite:")
        for uid in to_invite:
            print(f"  {uid}")
        return

    if not to_invite:
        print("All members already in target channel.")
        return

    invited = 0
    errors = 0
    batch_size = 30
    for i in range(0, len(to_invite), batch_size):
        batch = to_invite[i:i + batch_size]
        try:
            client.call(
                "conversations.invite",
                params={"channel": to_channel, "users": ",".join(batch)},
            )
            invited += len(batch)
        except Exception as e:
            errors += len(batch)
            print(f"  Error: {e}", file=sys.stderr)

    print(f"Done. Invited: {invited}, Errors: {errors}")


def export_members(
    client: SlackClient,
    channel: str,
    fmt: str = "table",
    as_json: bool = False,
) -> None:
    """Export channel members as CSV/JSON/markdown. Includes name and email."""
    member_ids = client.paginate(
        "conversations.members", params={"channel": channel}, response_key="members"
    )

    members = []
    for uid in member_ids:
        try:
            resp = client.call("users.info", params={"user": uid})
            user = resp.get("user", {})
            profile = user.get("profile", {})
            members.append({
                "id": uid,
                "name": user.get("real_name", profile.get("display_name", "")),
                "email": profile.get("email", ""),
                "is_bot": user.get("is_bot", False),
                "deleted": user.get("deleted", False),
            })
        except Exception:
            members.append({"id": uid, "name": "", "email": "", "is_bot": False, "deleted": False})

    if as_json or fmt == "json":
        print(json.dumps(members, indent=2))
        return

    if fmt == "csv":
        writer_io = io.StringIO()
        writer = csv.DictWriter(writer_io, fieldnames=["id", "name", "email", "is_bot", "deleted"])
        writer.writeheader()
        writer.writerows(members)
        print(writer_io.getvalue(), end="")
        return

    if fmt == "markdown":
        print("| ID | Name | Email | Bot | Deleted |")
        print("|---|---|---|---|---|")
        for m in members:
            print(f"| {m['id']} | {m['name']} | {m['email']} | {m['is_bot']} | {m['deleted']} |")
        print(f"\n*{len(members)} member(s)*")
        return

    # Default: table
    print(f"{'ID':<12} {'Name':<30} {'Email':<35} {'Bot'}")
    print("-" * 85)
    for m in members:
        print(f"{m['id']:<12} {m['name'][:28]:<30} {m['email'][:33]:<35} {'yes' if m['is_bot'] else 'no'}")
    print(f"\nTotal: {len(members)} member(s)")


def diff_channels(
    client: SlackClient,
    channel_a: str,
    channel_b: str,
    as_json: bool = False,
) -> None:
    """Compare membership of two channels."""
    members_a = set(
        client.paginate("conversations.members", params={"channel": channel_a}, response_key="members")
    )
    members_b = set(
        client.paginate("conversations.members", params={"channel": channel_b}, response_key="members")
    )

    only_a = sorted(members_a - members_b)
    only_b = sorted(members_b - members_a)
    in_both = sorted(members_a & members_b)

    if as_json:
        result = {
            "channel_a": channel_a,
            "channel_b": channel_b,
            "only_in_a": only_a,
            "only_in_b": only_b,
            "in_both": in_both,
        }
        print(json.dumps(result, indent=2))
        return

    print(f"Channel A: {channel_a} ({len(members_a)} members)")
    print(f"Channel B: {channel_b} ({len(members_b)} members)")
    print()
    print(f"Only in A ({len(only_a)}):")
    for uid in only_a:
        print(f"  {uid}")
    print()
    print(f"Only in B ({len(only_b)}):")
    for uid in only_b:
        print(f"  {uid}")
    print()
    print(f"In both ({len(in_both)}):")
    for uid in in_both:
        print(f"  {uid}")


def pick_random_member(
    client: SlackClient,
    channel: str,
    as_json: bool = False,
) -> None:
    """Pick a random non-bot member from a channel."""
    member_ids = client.paginate(
        "conversations.members", params={"channel": channel}, response_key="members"
    )

    # Filter out bots
    real_members = []
    for uid in member_ids:
        try:
            resp = client.call("users.info", params={"user": uid})
            user = resp.get("user", {})
            if not user.get("is_bot") and not user.get("deleted") and uid != "USLACKBOT":
                real_members.append(user)
        except Exception:
            pass

    if not real_members:
        print("No eligible members found.", file=sys.stderr)
        sys.exit(1)

    chosen = random.choice(real_members)
    profile = chosen.get("profile", {})

    if as_json:
        print(json.dumps(chosen, indent=2))
        return

    name = chosen.get("real_name", profile.get("display_name", chosen.get("id", "")))
    email = profile.get("email", "")
    print(f"Selected: {chosen.get('id', '')} - {name}")
    if email:
        print(f"  Email: {email}")
    print(f"\n(Chosen from {len(real_members)} eligible members)")


def list_inactive_members(
    client: SlackClient,
    channel: str,
    days: int = 30,
    dry_run: bool = False,
    as_json: bool = False,
) -> None:
    """List members who haven't posted in --days days."""
    cutoff_ts = time.time() - (days * 86400)

    # Get all member IDs
    member_ids = client.paginate(
        "conversations.members", params={"channel": channel}, response_key="members"
    )

    # Get recent message history to find active posters
    print(f"Checking activity for {len(member_ids)} members (past {days} days)...", file=sys.stderr)

    # Pull messages since cutoff
    try:
        resp = client.call(
            "conversations.history",
            params={"channel": channel, "oldest": str(cutoff_ts), "limit": 1000},
        )
        messages = resp.get("messages", [])
        # Handle pagination if needed
        while resp.get("has_more"):
            cursor = resp.get("response_metadata", {}).get("next_cursor", "")
            if not cursor:
                break
            resp = client.call(
                "conversations.history",
                params={"channel": channel, "oldest": str(cutoff_ts), "limit": 1000, "cursor": cursor},
            )
            messages.extend(resp.get("messages", []))
    except Exception as e:
        print(f"Warning: Could not fetch history: {e}", file=sys.stderr)
        messages = []

    # Collect active posters
    active_users = set()
    for msg in messages:
        uid = msg.get("user", "")
        if uid:
            active_users.add(uid)

    # Find inactive (exclude bots)
    inactive = []
    for uid in member_ids:
        if uid in active_users:
            continue
        try:
            resp = client.call("users.info", params={"user": uid})
            user = resp.get("user", {})
            if user.get("is_bot") or user.get("deleted") or uid == "USLACKBOT":
                continue
            profile = user.get("profile", {})
            inactive.append({
                "id": uid,
                "name": user.get("real_name", profile.get("display_name", uid)),
                "email": profile.get("email", ""),
            })
        except Exception:
            inactive.append({"id": uid, "name": "", "email": ""})

    if as_json:
        result = {
            "channel": channel,
            "days": days,
            "inactive_count": len(inactive),
            "inactive": inactive,
        }
        print(json.dumps(result, indent=2))
        return

    print(f"Channel: {channel}")
    print(f"Inactive (no posts in {days} days): {len(inactive)}")
    print()
    if dry_run:
        print("[DRY RUN] Would report:")
    print(f"{'ID':<12} {'Name':<30} {'Email'}")
    print("-" * 70)
    for m in inactive:
        print(f"{m['id']:<12} {m['name'][:28]:<30} {m['email']}")
