---
name: slack-post
description: "Post messages with Block Kit support. Covers simple text, threaded replies, Block Kit formatting, and scheduled messages. Use when sending Slack messages, building rich layouts, or scheduling posts."
command_name: slack-cli
tags: [slack, post, message, blocks, schedule, chat]
---
<!-- installed by slack-cli -->

# /slack-post -- Post Slack Messages with Block Kit

Send messages to Slack channels with plain text, rich Block Kit layouts, threaded replies, and scheduling.

## Arguments

- `/slack-post <channel> <message>` -- Post a simple text message
- `/slack-post` -- Interactive: ask for channel, message, and formatting

## Procedure

### Step 1: Simple Text Message

```bash
slack-cli chat post <channel> "Your message here"
```

The `<channel>` can be a channel ID (preferred) or channel name. Always prefer IDs for reliability.

```bash
# Post to a channel by ID
slack-cli chat post C08ACMRDC04 "Deploy completed successfully."

# Disable link previews (unfurling)
slack-cli chat post C08ACMRDC04 "Check https://example.com" --no-unfurl
```

### Step 2: Threaded Replies

Reply to an existing message by passing its timestamp:

```bash
slack-cli chat post <channel> "Thread reply here" --thread-ts 1234567890.123456
```

To find a message's timestamp, use `conversations history` or `chat permalink`:

```bash
# Get recent messages to find a ts value
slack-cli conversations history <channel> --limit 5 --json

# Then reply to it
slack-cli chat post <channel> "Following up on this" --thread-ts 1712345678.000100
```

### Step 3: Block Kit Messages

Use `--blocks` to send rich layouts. Blocks are a JSON array:

```bash
slack-cli chat post <channel> "Fallback text" --blocks '[
  {
    "type": "header",
    "text": {"type": "plain_text", "text": "Daily Report"}
  },
  {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Status:* All systems operational\n*Uptime:* 99.97%"}
  },
  {
    "type": "divider"
  },
  {
    "type": "section",
    "fields": [
      {"type": "mrkdwn", "text": "*Active Users*\n1,247"},
      {"type": "mrkdwn", "text": "*Requests/min*\n3,891"}
    ]
  }
]'
```

The `"Fallback text"` is shown in notifications and when blocks cannot render. Always include meaningful fallback text.

### Step 4: Scheduled Messages

Schedule a message for future delivery using a Unix timestamp:

```bash
# Schedule for a specific Unix timestamp
slack-cli chat schedule <channel> "Good morning team!" 1712400000

# With Block Kit
slack-cli chat schedule <channel> "Morning brief" 1712400000 --blocks '[...]'

# In a thread
slack-cli chat schedule <channel> "Follow-up" 1712400000 --thread-ts 1712345678.000100
```

To compute a Unix timestamp from a human-readable time:

```bash
# macOS
date -j -f "%Y-%m-%d %H:%M" "2026-04-11 09:00" "+%s"

# Linux
date -d "2026-04-11 09:00" "+%s"
```

### Step 5: Manage Scheduled Messages

```bash
# List all scheduled messages
slack-cli chat schedule-list --json

# List for a specific channel
slack-cli chat schedule-list --channel <channel> --json

# Cancel a scheduled message
slack-cli chat schedule-delete <channel> <scheduled_message_id>
```

## Block Kit Quick Reference

### Header Block

```json
{"type": "header", "text": {"type": "plain_text", "text": "Title Here"}}
```

### Section with Markdown

```json
{"type": "section", "text": {"type": "mrkdwn", "text": "*Bold* and _italic_ and `code`"}}
```

### Section with Fields (two-column layout)

```json
{
  "type": "section",
  "fields": [
    {"type": "mrkdwn", "text": "*Label 1*\nValue 1"},
    {"type": "mrkdwn", "text": "*Label 2*\nValue 2"}
  ]
}
```

### Divider

```json
{"type": "divider"}
```

### Context (small gray text, good for metadata)

```json
{
  "type": "context",
  "elements": [
    {"type": "mrkdwn", "text": "Posted by *Gigawatt* at 3:45 PM CST"}
  ]
}
```

### Actions (buttons)

```json
{
  "type": "actions",
  "elements": [
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "Approve"},
      "style": "primary",
      "action_id": "approve_action"
    },
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "Reject"},
      "style": "danger",
      "action_id": "reject_action"
    }
  ]
}
```

### Rich Text (preserves formatting exactly)

```json
{
  "type": "rich_text",
  "elements": [
    {
      "type": "rich_text_section",
      "elements": [
        {"type": "text", "text": "Regular text "},
        {"type": "text", "text": "bold text", "style": {"bold": true}}
      ]
    },
    {
      "type": "rich_text_list",
      "style": "bullet",
      "elements": [
        {"type": "rich_text_section", "elements": [{"type": "text", "text": "Item one"}]},
        {"type": "rich_text_section", "elements": [{"type": "text", "text": "Item two"}]}
      ]
    }
  ]
}
```

## Updating and Deleting Messages

```bash
# Update a posted message (need channel + message ts)
slack-cli chat update <channel> <ts> --text "Updated message text"

# Update with new blocks
slack-cli chat update <channel> <ts> --blocks '[...]'

# Delete a message
slack-cli chat delete <channel> <ts>

# Get permalink to a message
slack-cli chat permalink <channel> <ts>
```

## Tips

- **Slack mrkdwn is NOT standard Markdown.** Use `*bold*`, `_italic_`, `~strikethrough~`, `` `code` ``, and `> quote`. No `**bold**` or `# headings`.
- **Block Kit limit:** Max 50 blocks per message. Max 3000 chars per text field in a block.
- **Message length:** Max ~40,000 characters per message. Messages over ~4,000 chars may be truncated in some clients.
- **Fallback text matters:** Always provide meaningful text as the first argument alongside `--blocks`. This is what shows in notifications, search results, and accessibility tools.
- **Escaping in blocks JSON:** When passing blocks on the command line, use single quotes around the JSON to avoid shell interpretation. For complex blocks, write the JSON to a temp file and use `--blocks "$(cat /tmp/blocks.json)"`.
- **Schedule limits:** Scheduled messages must be at least 1 minute in the future and no more than 120 days out.
- **No em dashes in messages.** Use regular dashes or commas instead. Em dashes are an AI copywriting tell.
