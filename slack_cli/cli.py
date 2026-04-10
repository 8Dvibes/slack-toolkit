"""slack-cli: Zero-dependency CLI for the Slack Web API.

Entry point and argparse command tree.
"""

import argparse
import json
import sys
from typing import Optional

from . import __version__
from .client import SlackClient, SlackApiError
from .config import get_profile, require_profile, load_config, save_config


def _build_client(args) -> SlackClient:
    """Build a SlackClient from CLI args + config."""
    profile = require_profile(getattr(args, "profile", None))
    return SlackClient(
        bot_token=profile["bot_token"],
        user_token=profile.get("user_token", ""),
    )


# ---------------------------------------------------------------------------
# Config subcommands
# ---------------------------------------------------------------------------


def cmd_config_show(args):
    """Show current configuration."""
    config = load_config()
    if args.json:
        print(json.dumps(config, indent=2))
    else:
        default = config.get("default_profile", "default")
        profiles = config.get("profiles", {})
        print(f"Config file: ~/.slack-cli.json")
        print(f"Default profile: {default}")
        print(f"\nProfiles ({len(profiles)}):")
        for name, p in profiles.items():
            marker = " *" if name == default else ""
            wname = p.get("name", "")
            has_bot = "yes" if p.get("bot_token") else "no"
            has_user = "yes" if p.get("user_token") else "no"
            print(f"  {name}{marker}")
            if wname:
                print(f"    Workspace: {wname}")
            print(f"    Bot token: {has_bot}")
            print(f"    User token: {has_user}")
            if p.get("default_channel"):
                print(f"    Default channel: {p['default_channel']}")


def cmd_config_set_profile(args):
    """Create or update a profile."""
    config = load_config()
    profiles = config.setdefault("profiles", {})
    profile = profiles.get(args.name, {})

    if args.bot_token:
        profile["bot_token"] = args.bot_token
    if args.user_token:
        profile["user_token"] = args.user_token
    if args.workspace_name:
        profile["name"] = args.workspace_name
    if args.default_channel:
        profile["default_channel"] = args.default_channel

    profiles[args.name] = profile
    config["profiles"] = profiles
    save_config(config)
    print(f"Profile '{args.name}' saved.")


def cmd_config_set_default(args):
    """Set the default profile."""
    config = load_config()
    if args.name not in config.get("profiles", {}):
        print(f"Error: Profile '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    config["default_profile"] = args.name
    save_config(config)
    print(f"Default profile set to '{args.name}'.")


def cmd_config_remove_profile(args):
    """Remove a profile."""
    config = load_config()
    profiles = config.get("profiles", {})
    if args.name not in profiles:
        print(f"Error: Profile '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    del profiles[args.name]
    save_config(config)
    print(f"Profile '{args.name}' removed.")


# ---------------------------------------------------------------------------
# Chat subcommands
# ---------------------------------------------------------------------------


def cmd_chat_post(args):
    from .chat import post_message
    client = _build_client(args)
    post_message(
        client,
        channel=args.channel,
        text=args.text,
        blocks=args.blocks,
        thread_ts=args.thread_ts,
        unfurl_links=not args.no_unfurl,
        as_json=args.json,
    )


def cmd_chat_update(args):
    from .chat import update_message
    client = _build_client(args)
    update_message(
        client,
        channel=args.channel,
        ts=args.ts,
        text=args.text,
        blocks=args.blocks,
        as_json=args.json,
    )


def cmd_chat_delete(args):
    from .chat import delete_message
    client = _build_client(args)
    delete_message(client, channel=args.channel, ts=args.ts, as_json=args.json)


def cmd_chat_schedule(args):
    from .chat import schedule_message
    client = _build_client(args)
    schedule_message(
        client,
        channel=args.channel,
        text=args.text,
        post_at=args.post_at,
        blocks=args.blocks,
        thread_ts=args.thread_ts,
        as_json=args.json,
    )


def cmd_chat_schedule_delete(args):
    from .chat import delete_scheduled_message
    client = _build_client(args)
    delete_scheduled_message(
        client,
        channel=args.channel,
        scheduled_message_id=args.scheduled_message_id,
        as_json=args.json,
    )


def cmd_chat_schedule_list(args):
    from .chat import list_scheduled_messages
    client = _build_client(args)
    list_scheduled_messages(
        client,
        channel=getattr(args, "channel", None),
        as_json=args.json,
    )


def cmd_chat_permalink(args):
    from .chat import get_permalink
    client = _build_client(args)
    get_permalink(
        client,
        channel=args.channel,
        message_ts=args.message_ts,
        as_json=args.json,
    )


# ---------------------------------------------------------------------------
# Conversations subcommands
# ---------------------------------------------------------------------------


def cmd_conv_list(args):
    from .conversations import list_conversations
    client = _build_client(args)
    list_conversations(
        client,
        types=args.types,
        exclude_archived=not args.include_archived,
        limit=args.limit,
        as_json=args.json,
    )


def cmd_conv_info(args):
    from .conversations import get_info
    client = _build_client(args)
    get_info(client, channel=args.channel, as_json=args.json)


def cmd_conv_history(args):
    from .conversations import get_history
    client = _build_client(args)
    get_history(
        client,
        channel=args.channel,
        limit=args.limit,
        oldest=args.oldest,
        latest=args.latest,
        as_json=args.json,
    )


def cmd_conv_replies(args):
    from .conversations import get_replies
    client = _build_client(args)
    get_replies(
        client,
        channel=args.channel,
        ts=args.ts,
        limit=args.limit,
        as_json=args.json,
    )


def cmd_conv_members(args):
    from .conversations import get_members
    client = _build_client(args)
    get_members(
        client,
        channel=args.channel,
        limit=args.limit,
        as_json=args.json,
    )


def cmd_conv_create(args):
    from .conversations import create_conversation
    client = _build_client(args)
    create_conversation(
        client,
        name=args.name,
        is_private=args.private,
        as_json=args.json,
    )


def cmd_conv_archive(args):
    from .conversations import archive_conversation
    client = _build_client(args)
    archive_conversation(client, channel=args.channel, as_json=args.json)


def cmd_conv_unarchive(args):
    from .conversations import unarchive_conversation
    client = _build_client(args)
    unarchive_conversation(client, channel=args.channel, as_json=args.json)


def cmd_conv_invite(args):
    from .conversations import invite_to_conversation
    client = _build_client(args)
    invite_to_conversation(
        client,
        channel=args.channel,
        users=args.users,
        as_json=args.json,
    )


def cmd_conv_kick(args):
    from .conversations import kick_from_conversation
    client = _build_client(args)
    kick_from_conversation(
        client,
        channel=args.channel,
        user=args.user,
        as_json=args.json,
    )


def cmd_conv_topic(args):
    from .conversations import set_topic
    client = _build_client(args)
    set_topic(client, channel=args.channel, topic=args.topic, as_json=args.json)


def cmd_conv_purpose(args):
    from .conversations import set_purpose
    client = _build_client(args)
    set_purpose(
        client, channel=args.channel, purpose=args.purpose, as_json=args.json
    )


def cmd_conv_join(args):
    from .conversations import join_conversation
    client = _build_client(args)
    join_conversation(client, channel=args.channel, as_json=args.json)


def cmd_conv_leave(args):
    from .conversations import leave_conversation
    client = _build_client(args)
    leave_conversation(client, channel=args.channel, as_json=args.json)


# ---------------------------------------------------------------------------
# Users subcommands
# ---------------------------------------------------------------------------


def cmd_users_list(args):
    from .users import list_users
    client = _build_client(args)
    list_users(client, limit=args.limit, as_json=args.json)


def cmd_users_info(args):
    from .users import get_user_info
    client = _build_client(args)
    get_user_info(client, user=args.user, as_json=args.json)


def cmd_users_lookup(args):
    from .users import lookup_by_email
    client = _build_client(args)
    lookup_by_email(client, email=args.email, as_json=args.json)


def cmd_users_profile(args):
    from .users import get_profile as get_user_profile
    client = _build_client(args)
    get_user_profile(client, user=args.user, as_json=args.json)


def cmd_users_presence(args):
    from .users import get_presence
    client = _build_client(args)
    get_presence(client, user=args.user, as_json=args.json)


def cmd_users_set_presence(args):
    from .users import set_presence
    client = _build_client(args)
    set_presence(client, presence=args.presence, as_json=args.json)


# ---------------------------------------------------------------------------
# Search subcommands
# ---------------------------------------------------------------------------


def cmd_search_messages(args):
    from .search import search_messages
    client = _build_client(args)
    search_messages(
        client,
        query=args.query,
        sort=args.sort,
        sort_dir=args.sort_dir,
        count=args.count,
        as_json=args.json,
    )


def cmd_search_files(args):
    from .search import search_files
    client = _build_client(args)
    search_files(
        client,
        query=args.query,
        sort=args.sort,
        sort_dir=args.sort_dir,
        count=args.count,
        as_json=args.json,
    )


def cmd_search_all(args):
    from .search import search_all
    client = _build_client(args)
    search_all(
        client,
        query=args.query,
        sort=args.sort,
        sort_dir=args.sort_dir,
        count=args.count,
        as_json=args.json,
    )


# ---------------------------------------------------------------------------
# Files subcommands
# ---------------------------------------------------------------------------


def cmd_files_upload(args):
    from .files import upload_file
    client = _build_client(args)
    upload_file(
        client,
        filepath=args.filepath,
        channels=args.channels,
        title=args.title,
        initial_comment=args.comment,
        thread_ts=args.thread_ts,
        as_json=args.json,
    )


def cmd_files_list(args):
    from .files import list_files
    client = _build_client(args)
    list_files(
        client,
        channel=args.channel,
        user=args.user,
        types=args.types,
        count=args.count,
        as_json=args.json,
    )


def cmd_files_info(args):
    from .files import get_file_info
    client = _build_client(args)
    get_file_info(client, file_id=args.file_id, as_json=args.json)


def cmd_files_delete(args):
    from .files import delete_file
    client = _build_client(args)
    delete_file(client, file_id=args.file_id, as_json=args.json)


# ---------------------------------------------------------------------------
# Reactions subcommands
# ---------------------------------------------------------------------------


def cmd_reactions_add(args):
    from .reactions import add_reaction
    client = _build_client(args)
    add_reaction(
        client,
        channel=args.channel,
        timestamp=args.timestamp,
        name=args.name,
        as_json=args.json,
    )


def cmd_reactions_remove(args):
    from .reactions import remove_reaction
    client = _build_client(args)
    remove_reaction(
        client,
        channel=args.channel,
        timestamp=args.timestamp,
        name=args.name,
        as_json=args.json,
    )


def cmd_reactions_get(args):
    from .reactions import get_reactions
    client = _build_client(args)
    get_reactions(
        client,
        channel=args.channel,
        timestamp=args.timestamp,
        as_json=args.json,
    )


def cmd_reactions_list(args):
    from .reactions import list_reactions
    client = _build_client(args)
    list_reactions(
        client,
        user=args.user,
        count=args.count,
        as_json=args.json,
    )


# ---------------------------------------------------------------------------
# Pins subcommands
# ---------------------------------------------------------------------------


def cmd_pins_add(args):
    from .pins import add_pin
    client = _build_client(args)
    add_pin(client, channel=args.channel, timestamp=args.timestamp, as_json=args.json)


def cmd_pins_remove(args):
    from .pins import remove_pin
    client = _build_client(args)
    remove_pin(
        client, channel=args.channel, timestamp=args.timestamp, as_json=args.json
    )


def cmd_pins_list(args):
    from .pins import list_pins
    client = _build_client(args)
    list_pins(client, channel=args.channel, as_json=args.json)


# ---------------------------------------------------------------------------
# Bookmarks subcommands
# ---------------------------------------------------------------------------


def cmd_bookmarks_add(args):
    from .bookmarks import add_bookmark
    client = _build_client(args)
    add_bookmark(
        client,
        channel=args.channel,
        title=args.title,
        link=args.link,
        emoji=args.emoji,
        as_json=args.json,
    )


def cmd_bookmarks_edit(args):
    from .bookmarks import edit_bookmark
    client = _build_client(args)
    edit_bookmark(
        client,
        channel=args.channel,
        bookmark_id=args.bookmark_id,
        title=args.title,
        link=args.link,
        emoji=args.emoji,
        as_json=args.json,
    )


def cmd_bookmarks_list(args):
    from .bookmarks import list_bookmarks
    client = _build_client(args)
    list_bookmarks(client, channel=args.channel, as_json=args.json)


def cmd_bookmarks_remove(args):
    from .bookmarks import remove_bookmark
    client = _build_client(args)
    remove_bookmark(
        client,
        channel=args.channel,
        bookmark_id=args.bookmark_id,
        as_json=args.json,
    )


# ---------------------------------------------------------------------------
# API passthrough
# ---------------------------------------------------------------------------


def cmd_api(args):
    from .api import call_method
    client = _build_client(args)
    params = json.loads(args.params) if args.params else None
    call_method(
        client,
        method_name=args.method,
        params=params,
        token_type=args.token_type,
        as_json=True,  # Raw API always outputs JSON
    )


# ---------------------------------------------------------------------------
# Methods catalog
# ---------------------------------------------------------------------------


def cmd_methods_search(args):
    from .methods import cmd_search
    cmd_search(query=args.query, limit=args.limit, as_json=args.json)


def cmd_methods_get(args):
    from .methods import cmd_get
    cmd_get(name=args.name, as_json=args.json)


def cmd_methods_list(args):
    from .methods import cmd_list
    cmd_list(namespace=args.namespace, as_json=args.json)


def cmd_methods_namespaces(args):
    from .methods import cmd_namespaces
    cmd_namespaces(as_json=args.json)


def cmd_methods_update(args):
    from .methods import cmd_update
    cmd_update(as_json=args.json)


def cmd_methods_info(args):
    from .methods import cmd_info
    cmd_info(as_json=args.json)


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------


def cmd_skills_install(args):
    from .skills import install_skills
    install_skills(force=args.force)


def cmd_skills_list(args):
    from .skills import list_skills
    list_skills(as_json=args.json)


def cmd_skills_doctor(args):
    from .skills import doctor
    doctor()


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slack-cli",
        description="Zero-dependency CLI for the Slack Web API",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--profile", "-p", help="Config profile to use", default=None
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output as JSON"
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ---- config ----
    config_p = sub.add_parser("config", help="Manage configuration")
    config_sub = config_p.add_subparsers(dest="config_cmd")

    cs = config_sub.add_parser("show", help="Show current configuration")
    cs.set_defaults(func=cmd_config_show)

    csp = config_sub.add_parser("set-profile", help="Create or update a profile")
    csp.add_argument("name", help="Profile name")
    csp.add_argument("--bot-token", help="Bot token (xoxb-...)")
    csp.add_argument("--user-token", help="User token (xoxp-...)")
    csp.add_argument("--workspace-name", help="Workspace display name")
    csp.add_argument("--default-channel", help="Default channel ID")
    csp.set_defaults(func=cmd_config_set_profile)

    csd = config_sub.add_parser("set-default", help="Set default profile")
    csd.add_argument("name", help="Profile name")
    csd.set_defaults(func=cmd_config_set_default)

    crp = config_sub.add_parser("remove-profile", help="Remove a profile")
    crp.add_argument("name", help="Profile name")
    crp.set_defaults(func=cmd_config_remove_profile)

    # ---- chat ----
    chat_p = sub.add_parser("chat", help="Send and manage messages")
    chat_sub = chat_p.add_subparsers(dest="chat_cmd")

    cp = chat_sub.add_parser("post", help="Post a message")
    cp.add_argument("channel", help="Channel ID")
    cp.add_argument("text", help="Message text")
    cp.add_argument("--blocks", help="Block Kit blocks (JSON string)")
    cp.add_argument("--thread-ts", help="Thread timestamp to reply to")
    cp.add_argument("--no-unfurl", action="store_true", help="Disable link unfurling")
    cp.set_defaults(func=cmd_chat_post)

    cu = chat_sub.add_parser("update", help="Update a message")
    cu.add_argument("channel", help="Channel ID")
    cu.add_argument("ts", help="Message timestamp")
    cu.add_argument("--text", help="New text")
    cu.add_argument("--blocks", help="New blocks (JSON string)")
    cu.set_defaults(func=cmd_chat_update)

    cd = chat_sub.add_parser("delete", help="Delete a message")
    cd.add_argument("channel", help="Channel ID")
    cd.add_argument("ts", help="Message timestamp")
    cd.set_defaults(func=cmd_chat_delete)

    csc = chat_sub.add_parser("schedule", help="Schedule a message")
    csc.add_argument("channel", help="Channel ID")
    csc.add_argument("text", help="Message text")
    csc.add_argument("post_at", type=int, help="Unix timestamp to post at")
    csc.add_argument("--blocks", help="Block Kit blocks (JSON string)")
    csc.add_argument("--thread-ts", help="Thread timestamp")
    csc.set_defaults(func=cmd_chat_schedule)

    csdel = chat_sub.add_parser("schedule-delete", help="Delete a scheduled message")
    csdel.add_argument("channel", help="Channel ID")
    csdel.add_argument("scheduled_message_id", help="Scheduled message ID")
    csdel.set_defaults(func=cmd_chat_schedule_delete)

    csl = chat_sub.add_parser("schedule-list", help="List scheduled messages")
    csl.add_argument("--channel", help="Filter by channel ID")
    csl.set_defaults(func=cmd_chat_schedule_list)

    cpl = chat_sub.add_parser("permalink", help="Get message permalink")
    cpl.add_argument("channel", help="Channel ID")
    cpl.add_argument("message_ts", help="Message timestamp")
    cpl.set_defaults(func=cmd_chat_permalink)

    # ---- conversations ----
    conv_p = sub.add_parser("conversations", aliases=["conv"], help="Manage channels and DMs")
    conv_sub = conv_p.add_subparsers(dest="conv_cmd")

    cl = conv_sub.add_parser("list", help="List conversations")
    cl.add_argument(
        "--types",
        default="public_channel,private_channel",
        help="Comma-separated types (public_channel,private_channel,mpim,im)",
    )
    cl.add_argument("--include-archived", action="store_true")
    cl.add_argument("--limit", type=int, help="Max results")
    cl.set_defaults(func=cmd_conv_list)

    ci = conv_sub.add_parser("info", help="Get channel info")
    ci.add_argument("channel", help="Channel ID")
    ci.set_defaults(func=cmd_conv_info)

    ch = conv_sub.add_parser("history", help="Get message history")
    ch.add_argument("channel", help="Channel ID")
    ch.add_argument("--limit", type=int, default=100, help="Max messages")
    ch.add_argument("--oldest", help="Start timestamp")
    ch.add_argument("--latest", help="End timestamp")
    ch.set_defaults(func=cmd_conv_history)

    cr = conv_sub.add_parser("replies", help="Get thread replies")
    cr.add_argument("channel", help="Channel ID")
    cr.add_argument("ts", help="Thread parent timestamp")
    cr.add_argument("--limit", type=int, default=100, help="Max replies")
    cr.set_defaults(func=cmd_conv_replies)

    cm = conv_sub.add_parser("members", help="List channel members")
    cm.add_argument("channel", help="Channel ID")
    cm.add_argument("--limit", type=int, help="Max results")
    cm.set_defaults(func=cmd_conv_members)

    cc = conv_sub.add_parser("create", help="Create a channel")
    cc.add_argument("name", help="Channel name")
    cc.add_argument("--private", action="store_true", help="Create as private")
    cc.set_defaults(func=cmd_conv_create)

    ca = conv_sub.add_parser("archive", help="Archive a channel")
    ca.add_argument("channel", help="Channel ID")
    ca.set_defaults(func=cmd_conv_archive)

    cua = conv_sub.add_parser("unarchive", help="Unarchive a channel")
    cua.add_argument("channel", help="Channel ID")
    cua.set_defaults(func=cmd_conv_unarchive)

    cinv = conv_sub.add_parser("invite", help="Invite users to a channel")
    cinv.add_argument("channel", help="Channel ID")
    cinv.add_argument("users", help="Comma-separated user IDs")
    cinv.set_defaults(func=cmd_conv_invite)

    ck = conv_sub.add_parser("kick", help="Remove a user from a channel")
    ck.add_argument("channel", help="Channel ID")
    ck.add_argument("user", help="User ID to remove")
    ck.set_defaults(func=cmd_conv_kick)

    ct = conv_sub.add_parser("topic", help="Set channel topic")
    ct.add_argument("channel", help="Channel ID")
    ct.add_argument("topic", help="New topic text")
    ct.set_defaults(func=cmd_conv_topic)

    cpu = conv_sub.add_parser("purpose", help="Set channel purpose")
    cpu.add_argument("channel", help="Channel ID")
    cpu.add_argument("purpose", help="New purpose text")
    cpu.set_defaults(func=cmd_conv_purpose)

    cj = conv_sub.add_parser("join", help="Join a channel")
    cj.add_argument("channel", help="Channel ID")
    cj.set_defaults(func=cmd_conv_join)

    clv = conv_sub.add_parser("leave", help="Leave a channel")
    clv.add_argument("channel", help="Channel ID")
    clv.set_defaults(func=cmd_conv_leave)

    # ---- users ----
    users_p = sub.add_parser("users", help="User operations")
    users_sub = users_p.add_subparsers(dest="users_cmd")

    ul = users_sub.add_parser("list", help="List workspace users")
    ul.add_argument("--limit", type=int, help="Max results")
    ul.set_defaults(func=cmd_users_list)

    ui = users_sub.add_parser("info", help="Get user info")
    ui.add_argument("user", help="User ID")
    ui.set_defaults(func=cmd_users_info)

    ule = users_sub.add_parser("lookup", help="Look up user by email")
    ule.add_argument("email", help="Email address")
    ule.set_defaults(func=cmd_users_lookup)

    up = users_sub.add_parser("profile", help="Get user profile")
    up.add_argument("user", help="User ID")
    up.set_defaults(func=cmd_users_profile)

    upr = users_sub.add_parser("presence", help="Get user presence")
    upr.add_argument("user", help="User ID")
    upr.set_defaults(func=cmd_users_presence)

    usp = users_sub.add_parser("set-presence", help="Set bot presence")
    usp.add_argument("presence", choices=["auto", "away"], help="Presence status")
    usp.set_defaults(func=cmd_users_set_presence)

    # ---- search ----
    search_p = sub.add_parser("search", help="Search messages and files (requires user token)")
    search_sub = search_p.add_subparsers(dest="search_cmd")

    def _add_search_args(p):
        p.add_argument("query", help="Search query")
        p.add_argument("--sort", default="timestamp", choices=["timestamp", "score"])
        p.add_argument("--sort-dir", default="desc", choices=["asc", "desc"])
        p.add_argument("--count", type=int, default=20, help="Max results")

    sm = search_sub.add_parser("messages", help="Search messages")
    _add_search_args(sm)
    sm.set_defaults(func=cmd_search_messages)

    sf = search_sub.add_parser("files", help="Search files")
    _add_search_args(sf)
    sf.set_defaults(func=cmd_search_files)

    sa = search_sub.add_parser("all", help="Search messages and files")
    _add_search_args(sa)
    sa.set_defaults(func=cmd_search_all)

    # ---- files ----
    files_p = sub.add_parser("files", help="File operations")
    files_sub = files_p.add_subparsers(dest="files_cmd")

    fu = files_sub.add_parser("upload", help="Upload a file (V2 two-step flow)")
    fu.add_argument("filepath", help="Path to file")
    fu.add_argument("--channels", help="Comma-separated channel IDs to share to")
    fu.add_argument("--title", help="File title")
    fu.add_argument("--comment", help="Initial comment")
    fu.add_argument("--thread-ts", help="Thread timestamp")
    fu.set_defaults(func=cmd_files_upload)

    fl = files_sub.add_parser("list", help="List files")
    fl.add_argument("--channel", help="Filter by channel")
    fl.add_argument("--user", help="Filter by user")
    fl.add_argument("--types", help="Filter by type (e.g. images,pdfs)")
    fl.add_argument("--count", type=int, default=100, help="Max results")
    fl.set_defaults(func=cmd_files_list)

    fi = files_sub.add_parser("info", help="Get file info")
    fi.add_argument("file_id", help="File ID")
    fi.set_defaults(func=cmd_files_info)

    fd = files_sub.add_parser("delete", help="Delete a file")
    fd.add_argument("file_id", help="File ID")
    fd.set_defaults(func=cmd_files_delete)

    # ---- reactions ----
    react_p = sub.add_parser("reactions", aliases=["react"], help="Emoji reactions")
    react_sub = react_p.add_subparsers(dest="react_cmd")

    ra = react_sub.add_parser("add", help="Add a reaction")
    ra.add_argument("channel", help="Channel ID")
    ra.add_argument("timestamp", help="Message timestamp")
    ra.add_argument("name", help="Emoji name (without colons)")
    ra.set_defaults(func=cmd_reactions_add)

    rr = react_sub.add_parser("remove", help="Remove a reaction")
    rr.add_argument("channel", help="Channel ID")
    rr.add_argument("timestamp", help="Message timestamp")
    rr.add_argument("name", help="Emoji name (without colons)")
    rr.set_defaults(func=cmd_reactions_remove)

    rg = react_sub.add_parser("get", help="Get reactions on a message")
    rg.add_argument("channel", help="Channel ID")
    rg.add_argument("timestamp", help="Message timestamp")
    rg.set_defaults(func=cmd_reactions_get)

    rl = react_sub.add_parser("list", help="List reactions by a user")
    rl.add_argument("--user", help="User ID (default: authed user)")
    rl.add_argument("--count", type=int, default=100)
    rl.set_defaults(func=cmd_reactions_list)

    # ---- pins ----
    pins_p = sub.add_parser("pins", help="Pin operations")
    pins_sub = pins_p.add_subparsers(dest="pins_cmd")

    pa = pins_sub.add_parser("add", help="Pin a message")
    pa.add_argument("channel", help="Channel ID")
    pa.add_argument("timestamp", help="Message timestamp")
    pa.set_defaults(func=cmd_pins_add)

    pr = pins_sub.add_parser("remove", help="Unpin a message")
    pr.add_argument("channel", help="Channel ID")
    pr.add_argument("timestamp", help="Message timestamp")
    pr.set_defaults(func=cmd_pins_remove)

    pl = pins_sub.add_parser("list", help="List pinned items")
    pl.add_argument("channel", help="Channel ID")
    pl.set_defaults(func=cmd_pins_list)

    # ---- bookmarks ----
    bm_p = sub.add_parser("bookmarks", aliases=["bm"], help="Channel bookmarks")
    bm_sub = bm_p.add_subparsers(dest="bm_cmd")

    ba = bm_sub.add_parser("add", help="Add a bookmark")
    ba.add_argument("channel", help="Channel ID")
    ba.add_argument("title", help="Bookmark title")
    ba.add_argument("link", help="URL")
    ba.add_argument("--emoji", help="Emoji icon")
    ba.set_defaults(func=cmd_bookmarks_add)

    be = bm_sub.add_parser("edit", help="Edit a bookmark")
    be.add_argument("channel", help="Channel ID")
    be.add_argument("bookmark_id", help="Bookmark ID")
    be.add_argument("--title", help="New title")
    be.add_argument("--link", help="New URL")
    be.add_argument("--emoji", help="New emoji")
    be.set_defaults(func=cmd_bookmarks_edit)

    bl = bm_sub.add_parser("list", help="List bookmarks")
    bl.add_argument("channel", help="Channel ID")
    bl.set_defaults(func=cmd_bookmarks_list)

    brm = bm_sub.add_parser("remove", help="Remove a bookmark")
    brm.add_argument("channel", help="Channel ID")
    brm.add_argument("bookmark_id", help="Bookmark ID")
    brm.set_defaults(func=cmd_bookmarks_remove)

    # ---- api (raw passthrough) ----
    api_p = sub.add_parser(
        "api", help="Call any Slack API method directly (the escape hatch)"
    )
    api_p.add_argument("method", help="Slack API method name (e.g. chat.postMessage)")
    api_p.add_argument(
        "--params", help='JSON params string (e.g. \'{"channel":"C123","text":"hi"}\')'
    )
    api_p.add_argument(
        "--token-type",
        choices=["bot", "user", "auto"],
        default="bot",
        help="Which token to use",
    )
    api_p.set_defaults(func=cmd_api)

    # ---- methods catalog ----
    methods_p = sub.add_parser("methods", help="Browse the Slack API method catalog")
    methods_sub = methods_p.add_subparsers(dest="methods_cmd")

    ms = methods_sub.add_parser("search", help="Search methods by keyword")
    ms.add_argument("query", help="Search query")
    ms.add_argument("--limit", type=int, default=20, help="Max results")
    ms.set_defaults(func=cmd_methods_search)

    mg = methods_sub.add_parser("get", help="Get details for a method")
    mg.add_argument("name", help="Method name (e.g. chat.postMessage)")
    mg.set_defaults(func=cmd_methods_get)

    ml = methods_sub.add_parser("list", help="List all methods")
    ml.add_argument("--namespace", help="Filter by namespace (e.g. chat, conversations)")
    ml.set_defaults(func=cmd_methods_list)

    mn = methods_sub.add_parser("namespaces", help="List all API namespaces")
    mn.set_defaults(func=cmd_methods_namespaces)

    mu = methods_sub.add_parser("update", help="Update local method catalog")
    mu.set_defaults(func=cmd_methods_update)

    mi = methods_sub.add_parser("info", help="Show catalog status")
    mi.set_defaults(func=cmd_methods_info)

    # ---- skills ----
    skills_p = sub.add_parser("skills", help="Manage Claude Code skills")
    skills_sub = skills_p.add_subparsers(dest="skills_cmd")

    si = skills_sub.add_parser("install", help="Install skills to ~/.claude/skills/")
    si.add_argument("--force", action="store_true", help="Overwrite existing skills")
    si.set_defaults(func=cmd_skills_install)

    sls = skills_sub.add_parser("list", help="List bundled skills")
    sls.set_defaults(func=cmd_skills_list)

    sd = skills_sub.add_parser("doctor", help="Validate skills against CLI")
    sd.set_defaults(func=cmd_skills_doctor)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except SlackApiError as e:
        print(f"Error: {e.error}", file=sys.stderr)
        if e.body and isinstance(e.body, dict):
            metadata = e.body.get("response_metadata", {})
            if metadata.get("messages"):
                for msg in metadata["messages"]:
                    print(f"  {msg}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
