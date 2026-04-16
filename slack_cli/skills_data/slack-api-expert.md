---
name: slack-api-expert
description: "Learn slack-cli best practices. Token selection, pagination, rate limits, resolution chain. NOT errors (/slack-troubleshooting), NOT raw API (/slack-dynamic). Use when starting a new slack-cli task."
command_name: slack-cli
tags: [slack, api, expert, tokens, pagination, rate-limits, errors, source, meta, guide]
---
<!-- installed by slack-cli -->

# /slack-api-expert -- Master Guide for Using slack-cli

The definitive reference for AI agents using slack-cli. Covers how to think about the tool, not just what commands to type.

## The Self-Service Resolution Chain

Before asking a human or giving up, exhaust this chain in order:

```
1. Try the command  →  "Does a dedicated slack-cli command exist for this?"
2. Check the method catalog  →  "What Slack API method does this map to?"
3. Read the source  →  "How does this actually work internally?"
4. Use the dynamic pattern  →  "Call it raw via slack-cli api METHOD --params '{...}'"
```

### Step 1: Try the Dedicated Command

```bash
slack-cli --help                       # Top-level command list
slack-cli conversations --help         # Subcommand list
slack-cli chat --help
slack-cli users --help
slack-cli files --help
slack-cli reactions --help
slack-cli pins --help
```

Most common operations have dedicated commands. Start here.

### Step 2: Check the Method Catalog

If no dedicated command exists, find the raw API method:

```bash
slack-cli methods search <keyword>     # Search ~306 Slack API methods
slack-cli methods get <method.name>    # Get params, scopes, token type, rate tier
slack-cli methods namespaces           # Browse all API namespaces
slack-cli methods list --namespace conversations  # All methods in a namespace
```

### Step 3: Read the Source

**The CLI source is at `~/GitHub/slack-toolkit/slack_cli/`.** When you need to understand how a command works internally, read the source file directly. This is the opensrc pattern: give yourself access to the actual implementation, not just the docs.

Key files:
- `~/GitHub/slack-toolkit/slack_cli/cli.py` -- main CLI entry point, all command routing
- `~/GitHub/slack-toolkit/slack_cli/chat.py` -- post/update/delete/schedule messages
- `~/GitHub/slack-toolkit/slack_cli/conversations.py` -- channels: list, history, join, etc.
- `~/GitHub/slack-toolkit/slack_cli/users.py` -- user lookup, profile, presence
- `~/GitHub/slack-toolkit/slack_cli/files.py` -- file upload and listing
- `~/GitHub/slack-toolkit/slack_cli/reactions.py` -- add/remove/get reactions
- `~/GitHub/slack-toolkit/slack_cli/canvas.py` -- Slack canvas CRUD
- `~/GitHub/slack-toolkit/slack_cli/config.py` -- token management, profile handling
- `~/GitHub/slack-toolkit/slack_cli/methods.py` -- catalog search and method lookup
- `~/GitHub/slack-toolkit/slack_cli/api.py` -- raw API passthrough

When a command behaves unexpectedly, read the relevant source file. It is the ground truth.

### Step 4: Dynamic Pattern (Fallback for Any Method)

```bash
# Call any of the 306 Slack API methods directly
slack-cli api METHOD.NAME --params '{"key": "value"}' --json

# With user token
slack-cli api METHOD.NAME --params '{"key": "value"}' --token-type user --json
```

See `/slack-dynamic` for the full dynamic pattern walkthrough.

---

## Bot Token vs User Token

Most Slack API methods accept a **bot token** (`xoxb-`) and that is the default. Use `--token-type user` only when required.

### Use Bot Token (default) for:

- Posting messages (`chat.postMessage`)
- Reading channel history (`conversations.history`)
- Managing channels (`conversations.create`, `conversations.invite`)
- File uploads (`files.upload`)
- Reactions (`reactions.add`, `reactions.remove`)
- User lookup (`users.info`, `users.list`)
- Setting channel topic/purpose

### Use User Token (`--token-type user`) for:

- **Search** (`search.messages`, `search.files`) -- Slack search is always user-scoped
- **Reminders** (`reminders.add`, `reminders.list`) -- personal to the authed user
- **Do Not Disturb** (`dnd.setSnooze`, `dnd.endDnd`) -- personal state
- **Stars** (`stars.add`, `stars.remove`) -- personal bookmarks
- **Admin methods** (`admin.*`) -- requires user token with admin scopes
- **User profile writes** (`users.profile.set`) -- can only set your own profile

### How to Check Which Token a Method Needs

```bash
slack-cli methods get METHODNAME
```

Look for the `Token Types` line. It will say `bot`, `user`, or both.

### Quick Reference Table

| Method | Token | Notes |
|--------|-------|-------|
| chat.postMessage | bot | Default for all posting |
| conversations.history | bot | Reading channel messages |
| conversations.create | bot | Create a channel |
| search.messages | user | Search is always user-scoped |
| reminders.add | user | Personal reminders |
| dnd.setSnooze | user | Personal DND |
| admin.conversations.* | user | Admin API, needs admin scope |
| users.profile.set | user | Own profile only |
| files.upload | bot | File uploads |
| reactions.add | bot | Add emoji reactions |

---

## Pagination Patterns

### Automatic Pagination (Dedicated Commands)

Most dedicated slack-cli commands handle pagination automatically when you use `--limit` values higher than the API page size, or they expose a `--cursor` flag for manual page walking.

```bash
# These auto-paginate or return all results
slack-cli conversations list --limit 500
slack-cli users list --limit 1000
slack-cli conversations history CHANNEL --limit 200
```

### Manual Pagination (Raw API Passthrough)

The `slack-cli api` passthrough does NOT auto-paginate. You must loop manually.

```bash
# Page 1
slack-cli api conversations.history --params '{"channel": "C0123", "limit": 100}' --json

# The response contains response_metadata.next_cursor
# Extract it and pass as cursor on next call:
slack-cli api conversations.history --params '{"channel": "C0123", "limit": 100, "cursor": "CURSOR_VALUE"}' --json
```

### Checking if a Method Paginates

```bash
slack-cli methods get conversations.list
```

The output shows:
```
Paginated:    Yes (cursor key: channels)
```

The `cursor key` tells you which field in the response contains the data array (not the cursor itself -- the cursor is always in `response_metadata.next_cursor`).

### Pagination Shell Loop Pattern

```bash
CURSOR=""
while true; do
  if [ -z "$CURSOR" ]; then
    RESPONSE=$(slack-cli api conversations.list --params '{"limit": 200}' --json)
  else
    RESPONSE=$(slack-cli api conversations.list --params "{\"limit\": 200, \"cursor\": \"$CURSOR\"}" --json)
  fi
  echo "$RESPONSE" | python3 -c "import sys,json; data=json.load(sys.stdin); [print(c['id'], c['name']) for c in data.get('channels',[])]"
  CURSOR=$(echo "$RESPONSE" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('response_metadata',{}).get('next_cursor',''))" 2>/dev/null)
  [ -z "$CURSOR" ] && break
done
```

---

## Rate Limit Tiers

Slack rate limits are per-method per-workspace. slack-cli does not auto-retry on rate limits -- you must handle this if calling in bulk loops.

| Tier | Limit | Methods |
|------|-------|---------|
| Tier 1 | 1 call/min | Heavy admin calls |
| Tier 2 | 20 calls/min | Most admin methods |
| Tier 3 | 50 calls/min | Most read methods (conversations.history, users.list) |
| Tier 4 | 100 calls/min | High-frequency reads (reactions.get, pins.list) |
| Special | Varies | chat.postMessage (1 per second per channel) |

### Check a Method's Rate Tier

```bash
slack-cli methods get chat.postMessage
```

Output includes: `Rate Tier: Special (1/sec per channel)`

### Working Within Rate Limits

- For bulk operations across many channels, add `sleep 1` between iterations
- For Tier 1/2 methods (admin), always add a delay between calls
- `chat.postMessage` is 1 message/second per channel -- spread across channels if needed
- If you hit a rate limit, the Slack API response includes `Retry-After` in seconds

---

## Error Handling Patterns

### Common Errors and What They Mean

| Error | Meaning | Fix |
|-------|---------|-----|
| `not_authed` | Token missing or invalid | Check `slack-cli config show`, verify token is set |
| `invalid_auth` | Token exists but rejected | Rotate the token in Slack App dashboard |
| `channel_not_found` | Channel ID wrong or bot not in channel | Verify ID; join channel first |
| `not_in_channel` | Bot must be invited to channel | `slack-cli conversations join CHANNEL` |
| `missing_scope` | Token lacks a required OAuth scope | Add scope in Slack App dashboard, reinstall app |
| `not_allowed_token_type` | Bot token used for user-only method | Add `--token-type user` |
| `ratelimited` | Hit rate limit | Wait `Retry-After` seconds; reduce call frequency |
| `is_archived` | Channel is archived | Unarchive channel or use a different channel |
| `restricted_action` | Workspace admin policy blocks this | Report to workspace admin; cannot bypass |
| `invalid_blocks` | Block Kit JSON malformed | Validate at https://app.slack.com/block-kit-builder |
| `method_not_found` | Wrong method name | Double-check with `slack-cli methods search` |
| `invalid_arguments` | Required param missing or wrong type | Check `slack-cli methods get METHOD` for required params |
| `user_not_found` | User ID does not exist | Verify with `slack-cli users info USER_ID` |
| `no_text` | Message has no text content | Provide text content or use blocks with fallback text |

### Checking the Full Response for Errors

Always use `--json` with `slack-cli api` to see the full API response:

```bash
slack-cli api conversations.info --params '{"channel": "C0123"}' --json
# Response: {"ok": true, "channel": {...}}
# Or error: {"ok": false, "error": "channel_not_found"}
```

The `ok` field is the canonical success indicator. If `ok: false`, `error` has the specific error code.

### Scope Audit

To see what scopes your current token has:

```bash
slack-cli api auth.test --json
```

This returns your bot/user ID, workspace name, and the associated scopes.

---

## Most-Used Commands Quick Reference

| Task | Command |
|------|---------|
| Post a message | `slack-cli chat post CHANNEL "text"` |
| Post with blocks | `slack-cli chat post CHANNEL "fallback" --blocks '[...]'` |
| Reply in thread | `slack-cli chat post CHANNEL "text" --thread-ts TS` |
| Get channel history | `slack-cli conversations history CHANNEL --limit 20` |
| List channels | `slack-cli conversations list` |
| Join a channel | `slack-cli conversations join CHANNEL` |
| Look up a user | `slack-cli users info USER_ID` |
| Search for user | `slack-cli users lookup EMAIL` |
| Upload a file | `slack-cli files upload CHANNEL FILE` |
| Add a reaction | `slack-cli reactions add CHANNEL TS EMOJI` |
| Search messages | `slack-cli search messages "query"` |
| Check config | `slack-cli config show` |
| Call any method | `slack-cli api METHOD --params '{...}' --json` |
| Find a method | `slack-cli methods search KEYWORD` |
| Get method details | `slack-cli methods get METHOD.NAME` |

---

## Config and Token Setup

```bash
# Show current configuration
slack-cli config show

# Set bot token
slack-cli config set bot-token xoxb-YOUR-TOKEN-HERE

# Set user token (needed for user-scoped methods)
slack-cli config set user-token xoxp-YOUR-TOKEN-HERE

# Verify authentication
slack-cli api auth.test --json
```

The config is stored at `~/.slack-cli.json` (or the path shown by `slack-cli config show`).

---

## Source Reading Pattern

When you encounter unexpected behavior or need to understand internals, read the source. This is faster than experimenting and more accurate than guessing.

```bash
# What does conversations join actually do?
# Read: ~/GitHub/slack-toolkit/slack_cli/conversations.py

# How does config show work?
# Read: ~/GitHub/slack-toolkit/slack_cli/config.py

# What flags does chat post support?
# Read: ~/GitHub/slack-toolkit/slack_cli/chat.py
```

The source files are small and readable. Each file corresponds to one logical area of the API. Read the relevant file directly -- it will answer your question faster than any docs.

---

## Tips

- Always use channel IDs (e.g., `C0AM2BVMHRT`) rather than channel names. Names can change; IDs are permanent.
- The `--json` flag on any command outputs the raw Slack API response. Use it for scripting.
- When `slack-cli methods get METHOD` says `Deprecated: Yes`, check the description for the replacement method.
- For complex multi-step workflows, chain commands: get data → extract fields with `python3 -c` or `jq` → feed into next command.
- The method catalog is local (no network call). `methods search` and `methods get` are instant.
