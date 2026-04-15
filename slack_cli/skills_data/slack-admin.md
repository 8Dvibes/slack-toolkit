---
name: slack-admin
description: "Admin operations via slack-cli api passthrough: manage users, channels, apps, and workspace settings. Requires admin-level token."
command_name: slack-cli
tags: [slack, admin, workspace, enterprise, users, channels]
---
<!-- installed by slack-cli -->

# /slack-admin -- Admin Operations

Access Slack's admin API methods for workspace and organization management via `slack-cli api` passthrough.

## IMPORTANT: Admin Token Required

Admin methods require a token with admin-level scopes. These are NOT available on all Slack plans.
- Required token type: `xoxp-` (user token) with admin scopes
- Most methods need `admin:*` scopes
- Enterprise Grid plans have additional admin APIs

Configure your user token:
```bash
slack-cli config set-profile myprofile --user-token xoxp-YOUR-ADMIN-TOKEN
```

## Key Admin Operations

### User Management

```bash
# List all workspace users
slack-cli api admin.users.list --params '{"team_id": "T0XXXXXXXXX"}' --json

# Invite a user to the workspace
slack-cli api admin.users.invite --params '{
  "team_id": "T0XXXXXXXXX",
  "email": "newuser@example.com",
  "channel_ids": ["C0XXXXXXXXX"]
}'

# Set a user as admin
slack-cli api admin.users.setAdmin --params '{
  "team_id": "T0XXXXXXXXX",
  "user_id": "U0XXXXXXXXX"
}'

# Remove a user from the workspace
slack-cli api admin.users.remove --params '{
  "team_id": "T0XXXXXXXXX",
  "user_id": "U0XXXXXXXXX"
}'

# Set user expiration (for guest accounts)
slack-cli api admin.users.setExpiration --params '{
  "team_id": "T0XXXXXXXXX",
  "user_id": "U0XXXXXXXXX",
  "expiration_ts": 1775000000
}'
```

### Channel Management

```bash
# Create a channel (admin version -- can create private channels in other teams)
slack-cli api admin.conversations.create --params '{
  "name": "project-x",
  "is_private": false,
  "team_id": "T0XXXXXXXXX"
}'

# Archive a channel
slack-cli api admin.conversations.archive --params '{"channel_id": "C0XXXXXXXXX"}'

# Bulk archive channels
slack-cli api admin.conversations.bulkArchive --params '{
  "channel_ids": ["C0AAA", "C0BBB", "C0CCC"]
}'

# Search channels
slack-cli api admin.conversations.search --params '{
  "query": "project-",
  "team_ids": ["T0XXXXXXXXX"]
}'

# Get channel prefs
slack-cli api admin.conversations.getConversationPrefs --params '{
  "channel_id": "C0XXXXXXXXX"
}'
```

### App Management

```bash
# List approved apps
slack-cli api admin.apps.approved.list --params '{"team_id": "T0XXXXXXXXX"}' --json

# Approve an app
slack-cli api admin.apps.approve --params '{
  "app_id": "A0XXXXXXXXX",
  "team_id": "T0XXXXXXXXX"
}'

# Restrict an app
slack-cli api admin.apps.restrict --params '{
  "app_id": "A0XXXXXXXXX",
  "team_id": "T0XXXXXXXXX"
}'

# List pending app requests
slack-cli api admin.inviteRequests.list --params '{"team_id": "T0XXXXXXXXX"}'
```

### Workspace Settings

```bash
# Get workspace info
slack-cli api admin.teams.settings.info --params '{"team_id": "T0XXXXXXXXX"}' --json

# Set workspace name
slack-cli api admin.teams.settings.setName --params '{
  "team_id": "T0XXXXXXXXX",
  "name": "AI Build Lab"
}'

# List all workspaces (Enterprise Grid)
slack-cli api admin.teams.list --json
```

### Analytics

```bash
# Get daily analytics file (requires admin.analytics:read)
slack-cli api admin.analytics.getFile --params '{
  "type": "member",
  "date": "2026-04-12"
}' --json
```

## Safety Rules

- Admin operations are IRREVERSIBLE in many cases (remove user, delete channel).
- Always use `--json` and review the response before proceeding.
- For bulk operations (bulkArchive, bulkDelete), build and review the target list first.
- Never run admin operations on production workspaces without explicit authorization from the workspace owner.
