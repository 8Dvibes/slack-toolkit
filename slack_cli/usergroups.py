"""User group operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def create_usergroup(
    client: SlackClient,
    name: str,
    handle: Optional[str] = None,
    description: Optional[str] = None,
    channels: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Create a user group."""
    params = {"name": name}
    if handle:
        params["handle"] = handle
    if description:
        params["description"] = description
    if channels:
        params["channels"] = channels

    resp = client.call("usergroups.create", params=params)
    ug = resp.get("usergroup", {})

    if as_json:
        print(json.dumps(ug, indent=2))
        return

    print(f"Created: {ug.get('id', '')} - @{ug.get('handle', name)}")
    if description:
        print(f"  Description: {description}")


def list_usergroups(
    client: SlackClient,
    include_disabled: bool = False,
    include_users: bool = False,
    as_json: bool = False,
) -> None:
    """List all user groups."""
    params = {
        "include_disabled": include_disabled,
        "include_users": include_users,
    }
    resp = client.call("usergroups.list", params=params)
    groups = resp.get("usergroups", [])

    if as_json:
        print(json.dumps(groups, indent=2))
        return

    if not groups:
        print("No user groups found.")
        return

    print(f"{'ID':<12} {'Handle':<20} {'Name':<30} {'Users':<6} {'Enabled'}")
    print("-" * 80)
    for ug in groups:
        uid = ug.get("id", "")
        handle = "@" + ug.get("handle", "")
        ugname = ug.get("name", "")[:28]
        user_count = ug.get("user_count", 0)
        enabled = "yes" if not ug.get("date_delete", 0) else "no"
        print(f"{uid:<12} {handle:<20} {ugname:<30} {user_count:<6} {enabled}")
    print(f"\nTotal: {len(groups)} user group(s)")


def update_usergroup(
    client: SlackClient,
    usergroup: str,
    name: Optional[str] = None,
    handle: Optional[str] = None,
    description: Optional[str] = None,
    channels: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Update a user group."""
    params = {"usergroup": usergroup}
    if name:
        params["name"] = name
    if handle:
        params["handle"] = handle
    if description:
        params["description"] = description
    if channels:
        params["channels"] = channels

    resp = client.call("usergroups.update", params=params)
    ug = resp.get("usergroup", {})

    if as_json:
        print(json.dumps(ug, indent=2))
        return

    print(f"Updated: {ug.get('id', usergroup)} - @{ug.get('handle', '')}")


def disable_usergroup(
    client: SlackClient,
    usergroup: str,
    as_json: bool = False,
) -> None:
    """Disable a user group."""
    resp = client.call("usergroups.disable", params={"usergroup": usergroup})
    ug = resp.get("usergroup", {})

    if as_json:
        print(json.dumps(ug, indent=2))
        return

    print(f"Disabled: {usergroup}")


def enable_usergroup(
    client: SlackClient,
    usergroup: str,
    as_json: bool = False,
) -> None:
    """Enable a user group."""
    resp = client.call("usergroups.enable", params={"usergroup": usergroup})
    ug = resp.get("usergroup", {})

    if as_json:
        print(json.dumps(ug, indent=2))
        return

    print(f"Enabled: {usergroup}")


def list_usergroup_members(
    client: SlackClient,
    usergroup: str,
    include_disabled: bool = False,
    as_json: bool = False,
) -> None:
    """List members of a user group."""
    params = {"usergroup": usergroup, "include_disabled": include_disabled}
    resp = client.call("usergroups.users.list", params=params)
    users = resp.get("users", [])

    if as_json:
        print(json.dumps(users, indent=2))
        return

    if not users:
        print("No members found.")
        return

    for uid in users:
        print(f"  {uid}")
    print(f"\nTotal: {len(users)} member(s)")


def update_usergroup_members(
    client: SlackClient,
    usergroup: str,
    users: str,
    as_json: bool = False,
) -> None:
    """Set the members of a user group (replaces existing list)."""
    resp = client.call(
        "usergroups.users.update",
        params={"usergroup": usergroup, "users": users},
    )
    ug = resp.get("usergroup", {})

    if as_json:
        print(json.dumps(ug, indent=2))
        return

    user_count = ug.get("user_count", len(users.split(",")))
    print(f"Updated members of {usergroup}: {user_count} member(s)")
