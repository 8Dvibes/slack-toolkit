---
name: slack-identity
description: "Verify posting identity, check active token, audit scopes. Guardrails: always post as the configured bot, never impersonate users."
command_name: slack-cli
tags: [slack, identity, token, scopes, audit, security]
---
<!-- installed by slack-cli -->

# /slack-identity -- Verify Posting Identity

Check who you are posting as, verify the active token, and audit OAuth scopes before sending messages.

## CRITICAL GUARDRAILS

- **Always post as the bot.** Unless you have a user token AND explicit permission, all messages go through the bot identity.
- **Never impersonate a user.** Do not use `xoxp-` tokens to post "as" someone without their explicit consent.
- **Check before bulk operations.** Before posting to multiple channels, confirm the right profile is active.

## Procedure

### Step 1: Check the active profile

```bash
slack-cli config show
```

This shows which profile is active, the workspace name, and whether bot + user tokens are configured.

### Step 2: Verify the token is valid

```bash
# Check auth status (calls auth.test)
slack-cli api auth.test --json
```

The response will include:
- `user_id` -- the bot's user ID
- `user` -- the bot username
- `team` -- the workspace name
- `bot_id` -- confirms this is a bot token (not a user)

### Step 3: Audit scopes

```bash
# The X-OAuth-Scopes header in the auth.test response shows granted scopes
slack-cli api auth.test --json
```

Look for the `access_token` or check your profile config for the token type.

### Step 4: Verify you're posting as a bot (not a user)

```bash
slack-cli api auth.test --json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Posting as:', data.get('user'))
print('Bot ID:', data.get('bot_id', 'NONE -- this may be a user token!'))
print('Workspace:', data.get('team'))
print('User ID:', data.get('user_id'))
"
```

If `bot_id` is absent, you're using a user token. Confirm this is intentional.

### Step 5: Check scope coverage before calling an API method

```bash
# Look up required scopes for a method
slack-cli methods get chat.postMessage
# Shows: Required Scopes: bot: chat:write
```

## Common Issues

### "missing_scope" error

Your token doesn't have the required OAuth scope. Add the scope in your Slack app settings and reinstall.

### Posting as wrong identity

```bash
# Switch to a different profile
slack-cli --profile myotherprofile config show

# Or update the default
slack-cli config set-default myprofile
```

### Token is expired or revoked

```bash
slack-cli api auth.test --json
# Returns ok: false with error: "token_revoked" or "invalid_auth"
```

Update your token in the config:
```bash
slack-cli config set-profile myprofile --bot-token xoxb-NEW-TOKEN-HERE
```

## Scope Quick Reference

| Action | Required Scope |
|--------|---------------|
| Post messages | `chat:write` |
| Read channel history | `channels:history` or `groups:history` |
| List users | `users:read` |
| Manage usergroups | `usergroups:write` |
| Upload files | `files:write` |
| Read DMs | `im:history` |
| Search messages | `search:read` (user token only) |
| Manage reactions | `reactions:write` |

## Tips

- Always run `slack-cli api auth.test --json` at the start of any session that involves posting.
- For multi-workspace setups, name your profiles clearly: `prod`, `staging`, `dev`.
- Store bot tokens with `xoxb-` prefix -- never share them. User tokens start with `xoxp-`.
