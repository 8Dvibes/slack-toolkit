"""User operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def list_users(
    client: SlackClient,
    limit: Optional[int] = None,
    as_json: bool = False,
) -> None:
    """List all users in the workspace."""
    members = client.paginate(
        "users.list",
        limit=limit,
        response_key="members",
    )

    if as_json:
        print(json.dumps(members, indent=2))
        return

    if not members:
        print("No users found.")
        return

    print(f"{'ID':<15} {'Name':<25} {'Real Name':<30} {'Status'}")
    print("-" * 80)
    for u in members:
        uid = u.get("id", "")
        name = u.get("name", "")
        real_name = u.get("real_name", u.get("profile", {}).get("real_name", ""))
        deleted = u.get("deleted", False)
        is_bot = u.get("is_bot", False)
        status = ""
        if deleted:
            status = "deactivated"
        elif is_bot:
            status = "bot"
        elif u.get("is_admin"):
            status = "admin"
        elif u.get("is_owner"):
            status = "owner"
        print(f"{uid:<15} {name:<25} {real_name:<30} {status}")
    print(f"\nTotal: {len(members)} user(s)")


def get_user_info(
    client: SlackClient,
    user: str,
    as_json: bool = False,
) -> None:
    """Get info about a user."""
    resp = client.call("users.info", params={"user": user})
    u = resp.get("user", {})

    if as_json:
        print(json.dumps(u, indent=2))
        return

    profile = u.get("profile", {})
    print(f"ID:         {u.get('id', '')}")
    print(f"Name:       {u.get('name', '')}")
    print(f"Real Name:  {u.get('real_name', '')}")
    print(f"Display:    {profile.get('display_name', '')}")
    print(f"Email:      {profile.get('email', 'N/A')}")
    print(f"Title:      {profile.get('title', '')}")
    print(f"Status:     {profile.get('status_emoji', '')} {profile.get('status_text', '')}")
    print(f"Timezone:   {u.get('tz', '')} ({u.get('tz_label', '')})")
    print(f"Admin:      {u.get('is_admin', False)}")
    print(f"Bot:        {u.get('is_bot', False)}")
    print(f"Deleted:    {u.get('deleted', False)}")


def lookup_by_email(
    client: SlackClient,
    email: str,
    as_json: bool = False,
) -> None:
    """Look up a user by email address."""
    resp = client.call("users.lookupByEmail", params={"email": email})
    u = resp.get("user", {})

    if as_json:
        print(json.dumps(u, indent=2))
        return

    print(f"ID:         {u.get('id', '')}")
    print(f"Name:       {u.get('name', '')}")
    print(f"Real Name:  {u.get('real_name', '')}")
    print(f"Email:      {u.get('profile', {}).get('email', email)}")


def get_profile(
    client: SlackClient,
    user: str,
    as_json: bool = False,
) -> None:
    """Get a user's profile."""
    resp = client.call("users.profile.get", params={"user": user})
    profile = resp.get("profile", {})

    if as_json:
        print(json.dumps(profile, indent=2))
        return

    print(f"Display:    {profile.get('display_name', '')}")
    print(f"Real Name:  {profile.get('real_name', '')}")
    print(f"Email:      {profile.get('email', 'N/A')}")
    print(f"Title:      {profile.get('title', '')}")
    print(f"Phone:      {profile.get('phone', '')}")
    print(f"Status:     {profile.get('status_emoji', '')} {profile.get('status_text', '')}")
    print(f"Image:      {profile.get('image_72', '')}")


def set_presence(
    client: SlackClient,
    presence: str,
    as_json: bool = False,
) -> None:
    """Set the bot's presence. Must be 'auto' or 'away'."""
    resp = client.call("users.setPresence", params={"presence": presence})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Presence set to: {presence}")


def get_presence(
    client: SlackClient,
    user: str,
    as_json: bool = False,
) -> None:
    """Get a user's presence status."""
    resp = client.call("users.getPresence", params={"user": user})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Presence: {resp.get('presence', 'unknown')}")
    if resp.get("online"):
        print("Online:   Yes")
    if resp.get("auto_away"):
        print("Auto-away: Yes")
