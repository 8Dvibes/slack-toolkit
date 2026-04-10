---
name: slack-status
description: "Workspace health check: test connection, show bot info, list channels bot is in, show token scopes. Use when checking Slack connectivity, verifying bot setup, or getting an overview of the workspace."
command_name: slack-cli
tags: [slack, status, health, workspace, diagnostics]
---
<!-- installed by slack-cli -->

# /slack-status -- Slack Workspace Health Check

Run a comprehensive status check on the connected Slack workspace using `slack-cli`.

## Procedure

### Step 1: Test Authentication

```bash
slack-cli api auth.test --json
```

This returns the bot's identity: `user_id`, `team_id`, `team` (workspace name), `url`, and `bot_id`. If it fails, the token is invalid or expired.

### Step 2: Show Current Configuration

```bash
slack-cli config show
```

Displays the active profile, workspace name, and which tokens (bot/user) are configured. Verify both `bot_token` (xoxb-) and optionally `user_token` (xoxp-) are present.

### Step 3: List Channels the Bot Is In

```bash
slack-cli conversations list --json
```

This returns all conversations visible to the bot. Filter by type if needed:

```bash
# Only public channels
slack-cli conversations list --types public_channel --json

# Only private channels + group DMs
slack-cli conversations list --types private_channel,mpim --json

# Include archived channels
slack-cli conversations list --include-archived --json
```

### Step 4: Check Bot Token Scopes

The `auth.test` response does not include scopes directly. To inspect scopes, use the raw API call and check the response headers:

```bash
slack-cli api auth.test --json
```

The bot's effective permissions are determined by the scopes granted during app installation. If a command fails with `missing_scope`, the bot needs that scope added in the Slack App configuration.

### Step 5: Verify User Token (if configured)

If the profile has a user token, test it separately:

```bash
slack-cli api auth.test --token-type user --json
```

A user token (xoxp-) is required for search operations and some admin actions.

## Output Format

Present a concise dashboard:

```
## Slack Workspace Status

Connection: OK
Workspace: [team name] ([team_id])
Bot User: [bot name] ([user_id])
Bot ID: [bot_id]
Profile: [active profile name]

### Tokens
- Bot Token (xoxb-): Configured
- User Token (xoxp-): Configured / Not configured

### Channels (bot is a member)
| Channel | Type | Members | Topic |
|---------|------|---------|-------|
| #general | public | 42 | Welcome! |
| #ops | private | 5 | Ops alerts |

Total: N channels
```

## Multi-Profile Support

If the user has multiple workspaces configured, check a specific one:

```bash
slack-cli --profile <name> api auth.test --json
slack-cli --profile <name> conversations list --json
```

To see all configured profiles:

```bash
slack-cli config show
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `invalid_auth` | Token is invalid or revoked | Regenerate token in Slack App settings, run `slack-cli config set-profile` |
| `token_revoked` | App was uninstalled from workspace | Reinstall app, get new tokens |
| `missing_scope` on a command | Bot lacks required OAuth scope | Add scope in Slack App config, reinstall to workspace |
| `not_in_channel` | Bot is not a member of the target channel | Run `slack-cli conversations join <channel>` or invite the bot |
| No user token configured | Search and some admin features unavailable | Add `--user-token xoxp-...` when setting profile |

## Tips

- Run this at the start of any Slack automation session to verify connectivity before doing real work.
- If `conversations list` returns very few channels, the bot may need to be invited to more channels.
- Channel IDs (e.g., `C08ACMRDC04`) are stable. Channel names can change. Always use IDs in automation.
- The `--json` flag on any command gives machine-readable output for piping.
