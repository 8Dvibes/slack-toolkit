"""Do Not Disturb operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def get_dnd_info(
    client: SlackClient,
    user: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Get Do Not Disturb status for a user."""
    params = {}
    if user:
        params["user"] = user

    resp = client.call("dnd.info", params=params)

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    dnd_enabled = resp.get("dnd_enabled", False)
    snooze_enabled = resp.get("snooze_enabled", False)
    snooze_endtime = resp.get("snooze_endtime", 0)
    next_dnd_start = resp.get("next_dnd_start_ts", 0)
    next_dnd_end = resp.get("next_dnd_end_ts", 0)

    target = user or "authed user"
    print(f"DND Status for {target}:")
    print(f"  DND Enabled:    {dnd_enabled}")
    print(f"  Snooze Active:  {snooze_enabled}")
    if snooze_enabled and snooze_endtime:
        print(f"  Snooze Until:   {snooze_endtime} (Unix ts)")
    if next_dnd_start:
        print(f"  Next DND Start: {next_dnd_start}")
    if next_dnd_end:
        print(f"  Next DND End:   {next_dnd_end}")


def set_snooze(
    client: SlackClient,
    num_minutes: int,
    as_json: bool = False,
) -> None:
    """Turn on Do Not Disturb snooze for the authed user."""
    resp = client.call("dnd.setSnooze", params={"num_minutes": num_minutes})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    snooze_enabled = resp.get("snooze_enabled", True)
    snooze_endtime = resp.get("snooze_endtime", "")
    print(f"Snooze enabled for {num_minutes} minute(s).")
    if snooze_endtime:
        print(f"  Ends at: {snooze_endtime} (Unix ts)")


def end_snooze(
    client: SlackClient,
    as_json: bool = False,
) -> None:
    """End the authed user's currently active Do Not Disturb snooze."""
    resp = client.call("dnd.endSnooze")

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print("Snooze ended.")
    dnd_enabled = resp.get("dnd_enabled", False)
    print(f"  DND still active: {dnd_enabled}")


def end_dnd(
    client: SlackClient,
    as_json: bool = False,
) -> None:
    """End the authed user's Do Not Disturb session immediately."""
    resp = client.call("dnd.endDnd")

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print("DND session ended.")


def get_team_dnd_info(
    client: SlackClient,
    users: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Get DND status for multiple workspace members."""
    params = {}
    if users:
        params["users"] = users

    resp = client.call("dnd.teamInfo", params=params)
    team_info = resp.get("users", {})

    if as_json:
        print(json.dumps(team_info, indent=2))
        return

    if not team_info:
        print("No DND info returned.")
        return

    print(f"{'User ID':<15} {'DND':<6} {'Snooze':<8} {'Snooze Until'}")
    print("-" * 55)
    for uid, info in team_info.items():
        dnd = "yes" if info.get("dnd_enabled") else "no"
        snooze = "yes" if info.get("snooze_enabled") else "no"
        snooze_end = info.get("snooze_endtime", "")
        print(f"{uid:<15} {dnd:<6} {snooze:<8} {snooze_end}")
    print(f"\nTotal: {len(team_info)} user(s)")
