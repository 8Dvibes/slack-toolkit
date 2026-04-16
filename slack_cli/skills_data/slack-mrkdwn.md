---
name: slack-mrkdwn
description: "Reference for Slack mrkdwn syntax (NOT standard Markdown). Covers bold, italic, code, links, mentions, emoji, lists, blockquotes, date formatting, and escaping rules. Use when formatting message text for Slack."
command_name: slack-cli
tags: [slack, mrkdwn, markdown, formatting, text, mentions, emoji, links, dates, syntax]
---
<!-- installed by slack-cli -->

# /slack-mrkdwn -- Slack Mrkdwn Syntax Reference

Slack uses its own markup dialect called **mrkdwn** (note: no 'a'). It looks like Markdown but has critical differences. Use this when formatting message text in `section` blocks, `context` elements, or plain `chat post` messages.

---

## Core Formatting

| Effect | Syntax | Example |
|--------|--------|---------|
| Bold | `*text*` | `*Deploy complete*` |
| Italic | `_text_` | `_optional note_` |
| Strikethrough | `~text~` | `~deprecated~` |
| Inline code | `` `text` `` | `` `null` `` |
| Code block | ` ```text``` ` | multiline code |
| Blockquote | `>text` | quoted message |

**Bold:**
```
*This text will be bold*
```

**Italic:**
```
_This text will be italic_
```

**Strikethrough:**
```
~This is crossed out~
```

**Inline code:**
```
The error was `connection_refused` at line 47
```

**Code block** (triple backticks):
```
Here is the stack trace:
```
Error: ETIMEDOUT
  at TCPConnectWrap.connect (net.js:1141)
  at Socket.connect (net.js:878)
```
```

**Blockquote:**
```
> This is a quoted message
> It can span multiple lines
```

---

## Links

### URL with display text

```
<https://example.com|Click here>
```

Renders as: [Click here](https://example.com)

### Plain URL (auto-linked)

```
https://example.com
```

Slack auto-links bare URLs in message text.

### URL without label

```
<https://example.com>
```

Renders the URL as a clickable link without custom text.

---

## Mentions

### User mention

```
<@U07MBKFRLAG>
```

Renders as `@Tyler` (the user's display name). You need the user's Slack user ID (starts with `U`).

To find a user's ID:
```bash
slack-cli users lookup tyler@aibuildlab.com --json | python3 -c "import sys,json; print(json.load(sys.stdin)['user']['id'])"
```

### Channel mention

```
<#C0AM2BVMHRT>
```

Renders as `#gigawatt-lounge` (the channel name). Uses the channel ID.

### Special mentions

```
<!here>        # Notifies active channel members
<!channel>     # Notifies all channel members
<!everyone>    # Workspace-wide (only in #general)
```

Use `<!here>` and `<!channel>` sparingly -- they trigger notifications for everyone.

---

## Emoji

```
:emoji_name:
```

Standard Slack emoji names work. Custom workspace emoji also work if they exist.

Common emoji in agent messages:

| Emoji | Code | Use for |
|-------|------|---------|
| Green circle | `:large_green_circle:` | Healthy / OK |
| Yellow circle | `:large_yellow_circle:` | Warning / Degraded |
| Red circle | `:red_circle:` | Error / Down |
| Check mark | `:white_check_mark:` | Approved / Done |
| X | `:x:` | Rejected / Failed |
| Rotating light | `:rotating_light:` | Alert / Urgent |
| Information | `:information_source:` | Info / Note |
| Rocket | `:rocket:` | Deploy / Launch |
| Fire | `:fire:` | Hot / Breaking |
| Clock | `:clock3:` | Scheduled / Reminder |
| Robot | `:robot_face:` | Bot / Automated |

---

## Lists

Slack mrkdwn supports unordered and ordered lists in message text (not in Block Kit section fields -- use newlines with bullet characters there instead).

**Unordered list:**
```
- Item one
- Item two
- Item three
```

**Ordered list:**
```
1. First step
2. Second step
3. Third step
```

**Nested list** (indent with 4 spaces or a tab):
```
- Main item
    - Sub-item one
    - Sub-item two
- Another main item
```

**In Block Kit section fields**, lists don't auto-render. Use bullet characters manually:
```json
{"type": "mrkdwn", "text": "- Item one\n- Item two\n- Item three"}
```

---

## Date and Time Formatting

Slack renders Unix timestamps as formatted, localized dates using the `<!date>` tag. The viewer's local timezone is used automatically.

**Syntax:**
```
<!date^UNIX_TIMESTAMP^{FORMAT}|FALLBACK_TEXT>
```

**Format tokens:**

| Token | Output |
|-------|--------|
| `{date}` | September 18, 2026 |
| `{date_short}` | Sep 18, 2026 |
| `{date_long}` | Friday, September 18, 2026 |
| `{date_num}` | 09/18/2026 |
| `{time}` | 9:00 AM |
| `{time_secs}` | 9:00:23 AM |

**Examples:**
```
<!date^1713700000^{date_long} at {time}|April 21, 2026>
```
Renders as: "Monday, April 21, 2026 at 9:00 AM" in the viewer's timezone.

**Get current Unix timestamp:**
```bash
date +%s
```

**Getting a timestamp for a specific time:**
```bash
date -j -f "%Y-%m-%d %H:%M" "2026-04-21 09:00" "+%s"   # macOS
date -d "2026-04-21 09:00" "+%s"                         # Linux
```

---

## Differences from Standard Markdown

This is where agents make the most mistakes. Slack mrkdwn is NOT GitHub Markdown or CommonMark.

| Feature | Standard Markdown | Slack mrkdwn |
|---------|------------------|--------------|
| Bold | `**text**` | `*text*` |
| Italic | `*text*` or `_text_` | `_text_` only |
| Strikethrough | `~~text~~` | `~text~` |
| Heading | `# Heading` | No headings (use header block) |
| Image | `![alt](url)` | Use image block in Block Kit |
| Table | `| col | col |` | Not supported (use section fields) |
| Horizontal rule | `---` | Use divider block |
| Nested bold/italic | `**_text_**` | `*_text_*` works, but limited |
| HTML | `<b>text</b>` | Not rendered |
| Auto-link | `[text](url)` | `<url|text>` |

---

## Escaping Special Characters

If you need to include literal `<`, `>`, or `&` characters in message text (not as markup):

| Character | Escape |
|-----------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |

Example -- displaying code with angle brackets:
```
Use &lt;div class="foo"&gt; in your HTML
```

Renders as: `Use <div class="foo"> in your HTML`

---

## Common Formatting Patterns for Agent Messages

### Status line with emoji

```
:large_green_circle: *API Gateway* -- Healthy (142ms avg)
```

### Key-value pairs (in section text)

```
*Status:* Operational
*Version:* v2.4.1
*Region:* us-east-1
*Last deploy:* <!date^1713700000^{date_short} {time}|Apr 21 9:00 AM>
```

### Multi-item summary

```
*Completed tasks:*
- Deploy v2.4.1 to production :white_check_mark:
- Run database migrations :white_check_mark:
- Update load balancer config :white_check_mark:
- Send release notification :x:
```

### Agent attribution line (for context blocks)

```
Posted by *Gigawatt* | <!date^1713700000^{time}|9:00 AM> | <#C0AM2BVMHRT>
```

### Error message with code

```
:rotating_light: *Build failed in* `payments-service`

Error: `ETIMEDOUT` connecting to `api.stripe.com:443`

```
Retried 3 times (backoff: 1s, 2s, 4s)
All attempts failed
Last error at <!date^1713700000^{date_num} {time_secs}|2026-04-21>
```
```

### Thread summary

```
*Summary of discussion* (12 messages)

The team agreed to:
1. Defer the API v3 migration to next sprint
2. Proceed with the hotfix for the login bug
3. Schedule a post-mortem for Friday at 2 PM

_Next action: <@U07MBKFRLAG> to create tickets_
```

---

## Tips

- Test your formatting by posting to a private DM with yourself before posting to a channel
- Block Kit section `fields` arrays are two-column by default. They render well for key-value pairs but do not support inline code or complex formatting in the value
- Combining `*bold*` and `:emoji:` in the same field works fine
- Do not use em dashes (`--`). They are an AI copywriting tell. Use a regular dash (`-`) or restructure the sentence
- The `>` blockquote character must be at the start of the line -- it cannot be mid-sentence
- Nested code blocks (triple backticks inside backticks) do not work in mrkdwn
- Slack renders mrkdwn only in fields explicitly typed as `mrkdwn`. In `plain_text` typed fields, all markup shows as literal characters
