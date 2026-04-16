---
name: slack-troubleshooting
description: "Fix slack-cli errors and Slack API failures. Error code lookup, scope auditing, token debugging, diagnostic chain. NOT for learning slack-cli (/slack-api-expert). Use when a command fails or returns unexpected results."
command_name: slack-cli
tags: [slack, troubleshooting, errors, debugging, tokens, scopes, auth, diagnose]
---
<!-- installed by slack-cli -->

# /slack-troubleshooting -- Self-Diagnose and Fix Slack Errors

When something goes wrong with slack-cli, follow this skill before escalating to a human. Most errors are self-diagnosable and self-fixable.

---

## The Self-Service Debugging Chain

Exhaust these steps in order before asking for help:

```
1. Read the error code  →  Look it up in this skill
2. Check method spec    →  slack-cli methods get METHOD
3. Read the source      →  ~/GitHub/slack-toolkit/slack_cli/SOURCEFILE.py
4. Audit your scopes    →  slack-cli api auth.test --json
5. Escalate to human    →  Report exact error, command run, and what you tried
```

Always run commands with `--json` to get the full API response, which includes the exact error code.

---

## Error Code Reference

### `not_authed`

**Meaning:** No token provided, or token is missing from the request.

**Diagnosis:**
```bash
slack-cli config show
```

Check that `bot_token` and/or `user_token` are set.

**Fix:**
```bash
# Set bot token
slack-cli config set bot-token xoxb-YOUR-TOKEN

# Verify it works
slack-cli api auth.test --json
```

If `auth.test` returns `ok: true`, the token is valid. If it returns `invalid_auth`, the token is wrong.

---

### `invalid_auth`

**Meaning:** Token exists but Slack rejected it. Token is expired, revoked, or wrong.

**Diagnosis:**
```bash
slack-cli api auth.test --json
# Returns: {"ok": false, "error": "invalid_auth"}
```

**Fix:**
1. Go to your Slack App dashboard: https://api.slack.com/apps
2. Open your app > OAuth & Permissions
3. Reinstall the app to the workspace (generates a fresh token)
4. Update the token: `slack-cli config set bot-token xoxb-NEW-TOKEN`

---

### `channel_not_found`

**Meaning:** The channel ID or name you passed does not exist, or the bot cannot see it.

**Diagnosis:**
```bash
# Verify the channel exists and bot can see it
slack-cli api conversations.info --params '{"channel": "C0BADCHAN"}' --json
```

**Fix options:**

Option A -- Wrong channel ID: Verify the correct ID:
```bash
slack-cli conversations list --json | python3 -c "import sys,json; [print(c['id'], c['name']) for c in json.load(sys.stdin).get('channels',[])]"
```

Option B -- Bot not in channel: Join the channel:
```bash
slack-cli conversations join C0CHANNELID
```

Option C -- Private channel: The bot must be explicitly invited to private channels. Ask a member to invite the bot.

---

### `not_in_channel`

**Meaning:** The bot is not a member of the channel and cannot post/read.

**Fix:**
```bash
# Bot joins channel (works for public channels)
slack-cli conversations join C0CHANNELID

# For private channels, get a member to invite the bot
# (Bot user ID is shown in slack-cli api auth.test --json)
```

---

### `missing_scope`

**Meaning:** The token does not have the OAuth scope required for this method.

**Diagnosis -- check what scope is needed:**
```bash
slack-cli methods get METHOD.NAME
# Look for: "Required Scopes" section
```

**Diagnosis -- check what scopes you have:**
```bash
slack-cli api auth.test --json
# Returns scopes in the response headers (visible as xoauth_scopes in some responses)
```

**Fix:**
1. Go to Slack App dashboard > OAuth & Permissions
2. Under "Bot Token Scopes" or "User Token Scopes", add the missing scope
3. Reinstall the app (required after scope changes)
4. Update your token: `slack-cli config set bot-token xoxb-NEW-TOKEN`

**Common scope-method pairs:**

| Scope needed | Methods that need it |
|-------------|---------------------|
| `channels:read` | conversations.list (public channels) |
| `channels:write` | conversations.create, conversations.setTopic |
| `channels:history` | conversations.history (public channels) |
| `groups:history` | conversations.history (private channels) |
| `chat:write` | chat.postMessage |
| `files:write` | files.upload |
| `reactions:write` | reactions.add, reactions.remove |
| `users:read` | users.info, users.list |
| `users:read.email` | users.lookupByEmail |
| `search:read` | search.messages, search.files |
| `reminders:write` | reminders.add, reminders.delete |
| `admin` | admin.* methods |

---

### `not_allowed_token_type`

**Meaning:** You used a bot token (`xoxb-`) for a method that requires a user token (`xoxp-`), or vice versa.

**Diagnosis:**
```bash
slack-cli methods get METHOD.NAME
# Look for: "Token Types: user" (not bot)
```

**Fix:**
```bash
# Add --token-type user to your command
slack-cli api search.messages --params '{"query": "deploy"}' --token-type user --json
```

**Methods that always need user tokens:**
- `search.messages`, `search.files`
- `reminders.add`, `reminders.list`, `reminders.delete`
- `dnd.setSnooze`, `dnd.endDnd`, `dnd.endSnooze`
- `admin.*` methods (most of the admin namespace)
- `stars.add`, `stars.remove`

---

### `ratelimited`

**Meaning:** You hit Slack's rate limit for this method.

**How slack-cli handles it:** The CLI does NOT auto-retry on rate limits. You will see the error and need to handle it.

**The response includes a `Retry-After` value** in the response body (seconds to wait).

**Fix:**
```bash
# Wait the specified time, then retry
# For bulk operations, add sleep between calls:
for CHANNEL in $(cat channels.txt); do
  slack-cli chat post "$CHANNEL" "message"
  sleep 1  # 1 second between messages (Tier Special: 1/sec per channel)
done
```

**Rate tiers to know:**
- `chat.postMessage`: 1 per second per channel (Tier Special)
- Most read methods: 50 per minute (Tier 3)
- Admin methods: 20 per minute (Tier 2)

---

### `invalid_blocks`

**Meaning:** The Block Kit JSON you passed is malformed.

**Diagnosis:**
```bash
# Always use --json to see the full error
slack-cli chat post CHANNEL "fallback" --blocks '[...]' --json
# Returns: {"ok": false, "error": "invalid_blocks"}
```

**Common causes:**
- Missing required field (e.g., `text` object missing `type`)
- Using `mrkdwn` type in a `header` block (header requires `plain_text`)
- Invalid JSON (stray comma, unclosed bracket, unescaped character)
- Block array is not valid JSON (use single quotes around the JSON in shell)

**Fix:**
1. Validate visually: https://app.slack.com/block-kit-builder
2. Paste your blocks JSON, check the error panel
3. Fix the issue and re-run

**Shell quoting fix** (most common JSON error):
```bash
# WRONG: double quotes break with shell special characters
slack-cli chat post C1 "msg" --blocks "[{"type":"header"}]"

# CORRECT: single quotes protect the JSON
slack-cli chat post C1 "msg" --blocks '[{"type":"header","text":{"type":"plain_text","text":"Hi"}}]'

# ALSO CORRECT: file-based
cat > /tmp/b.json << 'EOF'
[{"type":"header","text":{"type":"plain_text","text":"Hi"}}]
EOF
slack-cli chat post C1 "msg" --blocks "$(cat /tmp/b.json)"
```

---

### `is_archived`

**Meaning:** The channel is archived and cannot receive new messages or be modified.

**Fix options:**
- Unarchive the channel: `slack-cli api conversations.unarchive --params '{"channel": "C0ARCHIVED"}'`
- Or use a different active channel

Note: Unarchiving requires the `channels:write` scope.

---

### `restricted_action`

**Meaning:** The workspace admin has a policy that prevents this action. This cannot be bypassed.

**Example causes:**
- Workspace requires admin approval for new channels
- File sharing is disabled by policy
- External sharing is blocked

**Action:**
Report to the workspace admin. This is a policy setting in Slack Admin dashboard. As an agent, you cannot override it.

---

### `user_not_found`

**Meaning:** The user ID you passed does not exist in the workspace.

**Fix:**
```bash
# Look up by email instead
slack-cli users lookup EMAIL --json

# Or search by name
slack-cli api users.list --params '{}' --json | python3 -c \
  "import sys,json; [print(u['id'], u.get('name',''), u.get('real_name','')) for u in json.load(sys.stdin).get('members',[])]"
```

---

### `no_text`

**Meaning:** You sent a message with `--blocks` but no fallback text argument.

**Fix:**
```bash
# WRONG -- missing fallback text
slack-cli chat post C1 --blocks '[...]'

# CORRECT -- provide fallback text as positional argument before --blocks
slack-cli chat post C1 "Fallback notification text" --blocks '[...]'
```

---

### `method_not_found`

**Meaning:** The method name you passed to `slack-cli api` does not exist in the Slack API.

**Fix:**
```bash
# Check the exact method name
slack-cli methods search KEYWORD

# Get the confirmed method name
slack-cli methods get conversations.open  # Example
```

Common typos: `conversation.history` (should be `conversations.history`), `chat.post` (should be `chat.postMessage`).

---

## Token Type Confusion

The two token types look similar but have different prefixes and permissions:

| Type | Prefix | Represents | Default |
|------|--------|-----------|---------|
| Bot token | `xoxb-` | Your Slack app's bot user | Yes (default) |
| User token | `xoxp-` | A human user who authorized your app | Use `--token-type user` |

**Check which token you're using:**
```bash
slack-cli config show
# Shows bot_token and user_token (if configured)
```

**Verify which token authenticates as what:**
```bash
# Check bot token
slack-cli api auth.test --json
# Returns: user_id (bot's user ID), bot_id, workspace name

# Check user token
slack-cli api auth.test --token-type user --json
# Returns: user_id (the human user's ID)
```

---

## Scope Audit

Full scope audit to understand what your tokens can do:

```bash
# Test both tokens and capture full response
echo "=== BOT TOKEN ==="
slack-cli api auth.test --json

echo "=== USER TOKEN ==="
slack-cli api auth.test --token-type user --json 2>/dev/null || echo "No user token configured"
```

The `auth.test` response includes workspace name, your bot/user IDs, and in some configurations the active scopes.

To see exactly what scopes were granted, check the OAuth page in your Slack App dashboard.

---

## Source Reading for Deep Debugging

When the error doesn't match any code above, read the source:

```bash
# What does the CLI actually send to Slack?
# Read the relevant command handler:
cat ~/GitHub/slack-toolkit/slack_cli/chat.py      # chat post issues
cat ~/GitHub/slack-toolkit/slack_cli/conversations.py  # conversations issues
cat ~/GitHub/slack-toolkit/slack_cli/config.py    # token/config issues
cat ~/GitHub/slack-toolkit/slack_cli/api.py       # raw passthrough issues
```

The source is small and readable. If the CLI is constructing the request wrong, you will see it immediately.

---

## Escalation Checklist

If you have exhausted all the above and still cannot resolve the issue, report:

1. The exact command you ran (sanitize the token)
2. The exact error response (from `--json` output)
3. The output of `slack-cli config show`
4. The output of `slack-cli api auth.test --json`
5. The method spec: `slack-cli methods get METHOD.NAME`
6. What you already tried from this skill

This gives a human everything needed to diagnose in one pass.
