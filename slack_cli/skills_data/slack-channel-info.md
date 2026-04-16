---
name: slack-channel-info
description: "Inspect a Slack channel in depth. Pulls info, members, messages, pins, bookmarks, topic, purpose. NOT for creating channels (/slack-channel-create). Use when investigating or building context on a channel."
command_name: slack-cli
tags: [slack, channel, info, members, pins, bookmarks, history]
---
<!-- installed by slack-cli -->

# /slack-channel-info -- Slack Channel Deep Dive

Get a complete picture of a Slack channel by combining info, members, recent messages, pins, and bookmarks into a single report.

## Arguments

- `/slack-channel-info <channel>` -- Full report on a channel (ID or name)

## Procedure

### Step 1: Get Channel Metadata

```bash
slack-cli conversations info <channel> --json
```

Key fields in the response:

- `channel.name` -- channel name
- `channel.id` -- channel ID
- `channel.topic.value` -- current topic
- `channel.purpose.value` -- channel purpose/description
- `channel.is_private` -- whether it is a private channel
- `channel.is_archived` -- whether it is archived
- `channel.num_members` -- member count
- `channel.created` -- Unix timestamp of creation
- `channel.creator` -- user ID of who created the channel

### Step 2: List Members

```bash
slack-cli conversations members <channel> --json
```

This returns a list of user IDs. To resolve names, look up each member:

```bash
# Get member list
slack-cli conversations members <channel> --json

# Look up each user (for small channels)
slack-cli users info <user_id> --json
```

For channels with many members, limit the lookup to avoid rate limits:

```bash
slack-cli conversations members <channel> --limit 50 --json
```

### Step 3: Get Recent Messages

```bash
# Last 20 messages
slack-cli conversations history <channel> --limit 20 --json

# Messages from a specific time range (Unix timestamps)
slack-cli conversations history <channel> --oldest 1712275200 --latest 1712361600 --json
```

To read a specific thread:

```bash
slack-cli conversations replies <channel> <thread_ts> --json
```

### Step 4: List Pins

```bash
slack-cli pins list <channel> --json
```

Pinned items include messages and files. Key fields:

- `items[].message.text` -- pinned message text
- `items[].message.ts` -- message timestamp
- `items[].message.user` -- who posted it

### Step 5: List Bookmarks

```bash
slack-cli bookmarks list <channel> --json
```

Bookmarks are saved links at the top of a channel. Key fields:

- `bookmarks[].title` -- bookmark display name
- `bookmarks[].link` -- the URL
- `bookmarks[].emoji` -- associated emoji (if any)

### Step 6: Compile the Report

Combine all the data into a single overview.

## Output Format

```
## Channel Report: #channel-name

**ID:** C08ACMRDC04
**Type:** Public / Private
**Created:** 2026-01-15 by @tyler
**Archived:** No
**Members:** 12

### Topic
Current channel topic text here

### Purpose
Channel purpose / description here

### Members (12)
| User | Name | Status |
|------|------|--------|
| U07MBKFRLAG | Tyler Fisk | Active |
| U07M6QW8DML | Sara Davison | Away |

### Pinned Items (3)
1. "Important announcement about..." -- @tyler (2026-03-15)
2. "Quarterly goals document" -- @sara (2026-02-28)

### Bookmarks (2)
1. [Project Dashboard](https://example.com/dashboard)
2. [Team Wiki](https://example.com/wiki)

### Recent Messages (last 10)
| Time | User | Message (truncated) |
|------|------|---------------------|
| 4:32 PM | @tyler | "Let's review the deploy..." |
| 4:15 PM | @sara | "Updated the config for..." |
```

## Related Operations

### Update Topic or Purpose

```bash
slack-cli conversations topic <channel> "New topic text"
slack-cli conversations purpose <channel> "New purpose text"
```

### Manage Pins

```bash
# Pin a message
slack-cli pins add <channel> <message_ts>

# Unpin a message
slack-cli pins remove <channel> <message_ts>
```

### Manage Bookmarks

```bash
# Add a bookmark
slack-cli bookmarks add <channel> "Dashboard" "https://example.com/dashboard" --emoji ":chart_with_upwards_trend:"

# Remove a bookmark (need bookmark_id from bookmarks list)
slack-cli bookmarks remove <channel> <bookmark_id>
```

### Channel Lifecycle

```bash
# Archive a channel
slack-cli conversations archive <channel>

# Unarchive a channel
slack-cli conversations unarchive <channel>

# Invite a user to the channel
slack-cli conversations invite <channel> <user_id>

# Remove a user from the channel
slack-cli conversations kick <channel> <user_id>
```

## Tips

- **Always use channel IDs** (e.g., `C08ACMRDC04`) instead of names. Names can change; IDs are permanent.
- **Member lookup is expensive.** For channels with 100+ members, avoid resolving every user ID to a name. Report the count and only resolve specific users when needed.
- **History time range.** The `--oldest` and `--latest` flags use Slack timestamps (Unix epoch with microsecond decimal). Use integer Unix timestamps for simplicity -- they work fine.
- **Thread awareness.** `conversations history` returns top-level messages only. If a message has `reply_count > 0`, use `conversations replies` to fetch the thread.
- **Rate limits.** Conversations API is Tier 3 (~50 requests/min for most methods). Batch your requests when building a channel report on a large channel.
- **Private channels.** The bot must be a member of private channels to access them. If you get `channel_not_found`, the bot may need to be invited.
