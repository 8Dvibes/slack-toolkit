---
name: slack-block-kit
description: "Build rich Slack messages with Block Kit. Covers block types, text objects, how to pass blocks via slack-cli, 5 ready-to-use templates, and common gotchas. Use when you need to post structured, visually formatted Slack messages."
command_name: slack-cli
tags: [slack, block-kit, blocks, rich-messages, formatting, templates, layouts, chat]
---
<!-- installed by slack-cli -->

# /slack-block-kit -- Build Rich Slack Messages with Block Kit

Block Kit is Slack's framework for building structured, visually rich messages. This skill teaches you how to design and send Block Kit messages using slack-cli.

**Block Kit Builder (visual designer):** https://app.slack.com/block-kit-builder

---

## Block Kit Structure

A Block Kit message is a JSON array of block objects. Each block has a `type` field that determines how it renders.

```bash
slack-cli chat post CHANNEL "Fallback text for notifications" --blocks '[
  {"type": "header", "text": {"type": "plain_text", "text": "Your Title"}},
  {"type": "section", "text": {"type": "mrkdwn", "text": "Body text here"}}
]'
```

The **fallback text** (the positional argument before `--blocks`) is shown in:
- Desktop notifications
- Mobile push notifications
- Search results
- Accessibility tools

Always make fallback text meaningful -- not just "message" or "notification."

---

## Block Types

### header

Large bold title. `plain_text` only (no markdown).

```json
{
  "type": "header",
  "text": {"type": "plain_text", "text": "Daily Operations Brief"}
}
```

### section

The workhorse block. Supports markdown body text and optional two-column fields.

```json
{
  "type": "section",
  "text": {"type": "mrkdwn", "text": "*Status:* All systems operational\n*Region:* us-east-1"}
}
```

Section with two-column fields (max 10 fields per section):

```json
{
  "type": "section",
  "fields": [
    {"type": "mrkdwn", "text": "*Active Users*\n1,247"},
    {"type": "mrkdwn", "text": "*Requests/min*\n3,891"},
    {"type": "mrkdwn", "text": "*Error Rate*\n0.02%"},
    {"type": "mrkdwn", "text": "*Avg Latency*\n142ms"}
  ]
}
```

### divider

Horizontal rule. No properties needed.

```json
{"type": "divider"}
```

### context

Small gray text. Great for metadata, timestamps, attribution.

```json
{
  "type": "context",
  "elements": [
    {"type": "mrkdwn", "text": "Posted by *Gigawatt* | 9:00 AM CST | <#C0AM2BVMHRT>"}
  ]
}
```

### actions

Interactive buttons. Note: buttons require a Slack app with interactivity enabled to handle click events. For read-only use (display without callbacks), they still render but clicks do nothing.

```json
{
  "type": "actions",
  "elements": [
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "Approve"},
      "style": "primary",
      "action_id": "approve_action",
      "value": "approved"
    },
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "Reject"},
      "style": "danger",
      "action_id": "reject_action",
      "value": "rejected"
    }
  ]
}
```

### image

Display an image inline.

```json
{
  "type": "image",
  "image_url": "https://example.com/chart.png",
  "alt_text": "Weekly traffic chart"
}
```

### rich_text

Full-fidelity text with nested formatting. More powerful than mrkdwn for complex layouts.

```json
{
  "type": "rich_text",
  "elements": [
    {
      "type": "rich_text_section",
      "elements": [
        {"type": "text", "text": "Build completed: ", "style": {"bold": true}},
        {"type": "text", "text": "v2.4.1"},
        {"type": "text", "text": " (3 warnings)"}
      ]
    },
    {
      "type": "rich_text_list",
      "style": "bullet",
      "elements": [
        {"type": "rich_text_section", "elements": [{"type": "text", "text": "Deprecated API usage in payments.js"}]},
        {"type": "rich_text_section", "elements": [{"type": "text", "text": "Missing error handler in worker.js"}]}
      ]
    }
  ]
}
```

---

## Text Objects

Every text-bearing field uses one of two object types:

| Type | Supports | Use For |
|------|----------|---------|
| `plain_text` | Plain text only | `header` blocks, button labels |
| `mrkdwn` | Slack mrkdwn formatting | `section` text, `context` elements |

Wrong type for the block causes a silent rendering failure or API error. `header` blocks **require** `plain_text` -- mrkdwn will not render there.

---

## Passing Blocks via slack-cli

### Single-line (small blocks)

```bash
slack-cli chat post C0AM2BVMHRT "Deploy complete" --blocks '[{"type":"header","text":{"type":"plain_text","text":"Deploy Complete"}},{"type":"section","text":{"type":"mrkdwn","text":"*Version:* v2.4.1\n*Duration:* 3m 22s"}}]'
```

### Multi-line (complex blocks, easier to read/debug)

```bash
slack-cli chat post C0AM2BVMHRT "Morning brief" --blocks '[
  {"type": "header", "text": {"type": "plain_text", "text": "Morning Brief"}},
  {"type": "section", "text": {"type": "mrkdwn", "text": "*Date:* Monday, April 14\n*Mood:* Operational"}},
  {"type": "divider"},
  {"type": "context", "elements": [{"type": "mrkdwn", "text": "Generated at 9:00 AM CST"}]}
]'
```

### From a file (for complex messages)

```bash
# Write blocks to file
cat > /tmp/blocks.json << 'EOF'
[
  {"type": "header", "text": {"type": "plain_text", "text": "Weekly Report"}},
  {"type": "section", "text": {"type": "mrkdwn", "text": "Here is your weekly summary..."}}
]
EOF

# Post using file
slack-cli chat post C0AM2BVMHRT "Weekly report" --blocks "$(cat /tmp/blocks.json)"
```

---

## 5 Ready-to-Use Templates

### Template 1: Simple Announcement

```bash
slack-cli chat post CHANNEL "Announcement: New release" --blocks '[
  {
    "type": "header",
    "text": {"type": "plain_text", "text": "New Release: v2.4.1"}
  },
  {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "The latest version is now live in production.\n\n*Highlights:*\n- Faster checkout flow\n- Bug fix for mobile login\n- Updated API rate limits"}
  },
  {
    "type": "context",
    "elements": [{"type": "mrkdwn", "text": "Released by <@U07MBKFRLAG> | April 14, 2026"}]
  }
]'
```

### Template 2: Status Update with Fields

```bash
slack-cli chat post CHANNEL "System status update" --blocks '[
  {
    "type": "header",
    "text": {"type": "plain_text", "text": "System Status"}
  },
  {
    "type": "section",
    "fields": [
      {"type": "mrkdwn", "text": "*API Gateway*\n:large_green_circle: Healthy"},
      {"type": "mrkdwn", "text": "*Database*\n:large_green_circle: Healthy"},
      {"type": "mrkdwn", "text": "*Worker Queue*\n:large_yellow_circle: Degraded"},
      {"type": "mrkdwn", "text": "*CDN*\n:large_green_circle: Healthy"}
    ]
  },
  {"type": "divider"},
  {
    "type": "section",
    "text": {"type": "mrkdwn", "text": ":large_yellow_circle: *Worker queue processing at 60% capacity.* Investigating."}
  },
  {
    "type": "context",
    "elements": [{"type": "mrkdwn", "text": "Last checked: 9:00 AM CST"}]
  }
]'
```

### Template 3: Approval Request

```bash
slack-cli chat post CHANNEL "Approval needed" --blocks '[
  {
    "type": "header",
    "text": {"type": "plain_text", "text": "Action Required: Approval Needed"}
  },
  {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Request:* Deploy v2.4.1 to production\n*Requester:* <@U07MBKFRLAG>\n*Impact:* ~5 min maintenance window\n*Rollback plan:* Auto-rollback on error rate > 1%"}
  },
  {"type": "divider"},
  {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "React :white_check_mark: to approve or :x: to reject.\nOr reply in this thread with your decision."}
  },
  {
    "type": "context",
    "elements": [{"type": "mrkdwn", "text": "Requested at 2:34 PM CST | Expires in 1 hour"}]
  }
]'
```

### Template 4: Report with Table-Like Sections

```bash
slack-cli chat post CHANNEL "Weekly metrics report" --blocks '[
  {
    "type": "header",
    "text": {"type": "plain_text", "text": "Weekly Metrics Report"}
  },
  {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "Week of April 7-13, 2026"}
  },
  {"type": "divider"},
  {
    "type": "section",
    "fields": [
      {"type": "mrkdwn", "text": "*New Students*\n47"},
      {"type": "mrkdwn", "text": "*vs Last Week*\n+12%"},
      {"type": "mrkdwn", "text": "*Revenue*\n$14,230"},
      {"type": "mrkdwn", "text": "*vs Last Week*\n+8%"},
      {"type": "mrkdwn", "text": "*Support Tickets*\n23"},
      {"type": "mrkdwn", "text": "*Resolved*\n21 (91%)"}
    ]
  },
  {"type": "divider"},
  {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Top channels:* #foundations-c18 (142 msgs), #docgen-c7 (89 msgs)"}
  },
  {
    "type": "context",
    "elements": [{"type": "mrkdwn", "text": "Generated by Gigawatt | Full report in <#C0AM2BVMHRT>"}]
  }
]'
```

### Template 5: Error Alert

```bash
slack-cli chat post CHANNEL "Error: Build failed" --blocks '[
  {
    "type": "header",
    "text": {"type": "plain_text", "text": ":rotating_light: Build Failed"}
  },
  {
    "type": "section",
    "fields": [
      {"type": "mrkdwn", "text": "*Workflow*\nn8n-deploy-production"},
      {"type": "mrkdwn", "text": "*Node*\nHTTP Request"},
      {"type": "mrkdwn", "text": "*Error*\n`connection timeout`"},
      {"type": "mrkdwn", "text": "*Time*\n2:47 PM CST"}
    ]
  },
  {"type": "divider"},
  {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "```\nError: ETIMEDOUT connecting to api.example.com:443\nRetried 3 times, all failed\nLast attempt: 2026-04-14T14:47:03Z\n```"}
  },
  {
    "type": "context",
    "elements": [{"type": "mrkdwn", "text": ":information_source: Check the workflow execution log for full trace."}]
  }
]'
```

---

## Common Gotchas

- **Max 50 blocks per message.** Split long reports into multiple messages or use threads.
- **Max 3,000 characters per text field.** Truncate or summarize long content.
- **Max 40,000 characters per message total.** Very rare limit but exists.
- **Header blocks require `plain_text`.** Mrkdwn in a header silently renders as plain text or errors.
- **Mrkdwn is NOT standard Markdown.** Use `*bold*` not `**bold**`, `_italic_` not `*italic*`, `~strike~` not `~~strike~~`. No `# headings`.
- **Buttons do not self-handle.** Without a Slack interactivity endpoint, buttons render but clicking them sends nothing.
- **Emoji in `plain_text` fields** use `:emoji_name:` syntax and work fine.
- **Fallback text is required** when using `--blocks`. Without it, the Slack API returns `no_text`.
- **Shell quoting:** Use single quotes around the JSON to avoid shell interpretation of `$` and `!` characters. If your JSON contains single quotes, use `--blocks "$(cat /tmp/blocks.json)"` instead.
- **No em dashes (`--`) in message text.** They are an AI copywriting tell. Use regular dashes.

---

## Validate Blocks Before Sending

Use the Block Kit Builder to visually design and validate before running the command:

1. Go to https://app.slack.com/block-kit-builder
2. Paste your blocks JSON
3. Preview renders immediately
4. Fix any errors shown in the validator panel
5. Copy validated JSON and use in your slack-cli command

Alternatively, check for `invalid_blocks` in the API response (always use `--json` to see it):

```bash
slack-cli chat post CHANNEL "test" --blocks '[...]' --json
# Check: {"ok": false, "error": "invalid_blocks"}
```
