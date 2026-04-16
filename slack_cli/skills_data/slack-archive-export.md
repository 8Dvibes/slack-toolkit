---
name: slack-archive-export
description: "Export Slack channel history to markdown. Fetches messages with date ranges, resolves usernames, handles pagination. Use when archiving a channel, exporting a conversation log, or backing up history before archiving."
command_name: slack-cli
tags: [slack, archive, export, history, markdown]
---
<!-- installed by slack-cli -->

# /slack-archive-export -- Export Channel History to Markdown

Fetch Slack channel history and format it as clean, readable markdown using `slack-cli`.

## When to Use

- Archiving a channel's conversation history
- Exporting a date range of messages for documentation
- Creating a readable log of a channel for review
- Backing up important conversations before archiving a channel
- Building a knowledge base from Slack discussions

## Procedure

### Step 1: Identify the Channel

If you have a channel name but not the ID:

```bash
slack-cli conversations list --json
```

Find the channel in the output. You need the `id` field (e.g., `C0AM2BVMHRT`).

Or get detailed info about a specific channel:

```bash
slack-cli conversations info <CHANNEL_ID> --json
```

### Step 2: Determine the Date Range

Slack uses Unix timestamps for `--oldest` and `--latest`. Convert dates:

```bash
# macOS
date -j -f "%Y-%m-%d %H:%M:%S" "2026-04-01 00:00:00" "+%s"

# Linux
date -d "2026-04-01 00:00:00" "+%s"
```

Or use Python:

```python
from datetime import datetime
int(datetime(2026, 4, 1).timestamp())  # 1774947600
```

### Step 3: Fetch the History

```bash
slack-cli conversations history <CHANNEL_ID> --json --limit 1000
```

With a date range:

```bash
slack-cli conversations history <CHANNEL_ID> --json --limit 1000 --oldest 1774947600 --latest 1775552400
```

The `--limit` flag caps at 1000 per call (Slack API limit). For channels with more messages, see the pagination section below.

### Step 4: Build a User Lookup Table

Messages contain user IDs, not names. Build a lookup:

```bash
slack-cli users list --json
```

This returns all workspace users. Extract `id` and `real_name` (or `profile.display_name`) to map IDs to names.

For a single user:

```bash
slack-cli users info <USER_ID> --json
```

### Step 5: Format as Markdown

Process the JSON output into markdown. For each message:

1. Convert the `ts` field (Unix timestamp string like `"1712345678.123456"`) to a human-readable datetime
2. Replace the `user` ID with the resolved display name
3. Preserve the `text` field (already in Slack mrkdwn, which is close to markdown)
4. Note thread indicators: if `reply_count` > 0, mark it as a thread parent
5. Optionally fetch thread replies for threaded messages

Target format:

```markdown
# #channel-name Export (2026-04-01 to 2026-04-07)

## 2026-04-01

**[09:15 AM] Tyler Fisk:**
Hey team, here is the plan for this week...

> 3 replies in thread

**[09:22 AM] Sara Davison:**
Looks good! I will start on the first item.

**[10:45 AM] Wade:**
Quick question about the timeline...

---

## 2026-04-02

**[08:30 AM] Tyler Fisk:**
Morning update: ...
```

### Step 6: Handle Pagination for Large Histories

If the channel has more than 1000 messages in your date range, you need to paginate. The conversations.history response includes `has_more` and the last message's `ts` can be used as the next `--latest`:

```bash
# First batch
slack-cli conversations history <CHANNEL_ID> --json --limit 1000 --oldest 1774947600

# Check if has_more is true in the response, then use the oldest ts from results as --latest
slack-cli conversations history <CHANNEL_ID> --json --limit 1000 --oldest 1774947600 --latest <LAST_TS_FROM_PREV_BATCH>
```

Note: Messages come back in reverse chronological order (newest first). When paginating, use the `ts` of the **last** (oldest) message in each batch as `--latest` for the next call.

Alternatively, use the raw API for cursor-based pagination:

```bash
slack-cli api conversations.history --params '{"channel":"C123","limit":200,"cursor":"<next_cursor>"}'
```

### Step 7: Include Thread Content (Optional)

For messages with `reply_count > 0`, fetch the thread:

```bash
slack-cli conversations replies <CHANNEL_ID> <THREAD_TS> --json
```

Format thread replies as indented or nested under the parent:

```markdown
**[09:15 AM] Tyler Fisk:**
Hey team, here is the plan for this week...

> **[09:18 AM] Sara:** Which item is highest priority?
> **[09:20 AM] Tyler:** The first one, for sure.
> **[09:22 AM] Sara:** On it.
```

## Example: Full Export Script

```bash
# 1. Fetch history
slack-cli conversations history C0AM2BVMHRT --json --limit 1000 --oldest 1774947600 --latest 1775552400 > /tmp/history.json

# 2. Fetch user list for name resolution
slack-cli users list --json > /tmp/users.json

# 3. Process with Python/jq to produce markdown
# (write a small script to join users.json names with history.json messages)
```

## Tips

- Always use `--json` for export. The human-readable format truncates messages to 120 characters.
- Slack mrkdwn uses `*bold*`, `_italic_`, `~strike~`, `` `code` ``, and ` ```code block``` `. These translate closely to standard markdown but not identically -- `*bold*` in Slack is `**bold**` in markdown.
- User mentions in text appear as `<@U07MBKFRLAG>`. Replace these with the resolved display name during formatting.
- Channel references appear as `<#C0AM2BVMHRT|channel-name>`. Extract the name after the pipe.
- Links appear as `<https://example.com|display text>` or just `<https://example.com>`.
- Bot messages have `bot_id` instead of `user`. Use `slack-cli users info <BOT_ID>` or check the `username` field.
- File attachments are referenced in the `files` array of each message. Export the file metadata (name, URL) even if you do not download the files themselves.
- For very large exports (10,000+ messages), batch the work in date chunks (one week at a time) to avoid memory issues.
