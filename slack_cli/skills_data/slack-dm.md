---
name: slack-dm
description: "Open DMs and group DMs in Slack. Resolves emails to user IDs, opens 1:1 or multi-party conversations. NOT for channel posts (/slack-post). Use when you need to send a direct message to one or more users."
command_name: slack-cli
tags: [slack, dm, direct-message, group-dm, conversations]
---
<!-- installed by slack-cli -->

# /slack-dm -- Create and Manage DMs

Open DMs and group DMs in Slack. Accepts user IDs or email addresses.

## Arguments

- `/slack-dm <user>` -- Open a DM with one user (ID or email)
- `/slack-dm` -- Interactive: ask who to DM and what to send

## Procedure

### Step 1: Open a DM by user ID

```bash
slack-cli conversations open --users U07MBKFRLAG
```

### Step 2: Open a group DM

```bash
slack-cli conversations open --users U07MBKFRLAG,U07M6QW8DML,U07MV3K3203
```

### Step 3: Resolve emails to IDs first

If you have an email instead of a user ID:

```bash
# Look up one user
slack-cli users lookup someone@example.com --json

# Or let conversations open resolve it automatically
slack-cli conversations open --users someone@example.com
```

The `conversations open` command automatically resolves emails via `users.lookupByEmail`.

### Step 4: Send a message to the opened DM

Once you have the DM channel ID from the `open` response:

```bash
# Get the channel ID from --json output
CHANNEL_ID=$(slack-cli conversations open --users U07MBKFRLAG --json | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")

# Send a message
slack-cli chat post $CHANNEL_ID "Hey, wanted to follow up on that task."
```

## Worked Examples

### Send a DM to Tyler

```bash
slack-cli conversations open --users U07MBKFRLAG --json
# Returns: {"id": "D0XXXXXXXXX", "is_im": true, ...}
slack-cli chat post D0XXXXXXXXX "Hey Tyler, the build is done."
```

### Start a group DM with Tyler, Sara, and Wade

```bash
slack-cli conversations open --users U07MBKFRLAG,U07M6QW8DML,U07MV3K3203 --json
slack-cli chat post C_GROUP_DM_ID "Team, quick sync needed."
```

### DM someone by email

```bash
slack-cli conversations open --users tyler@aibuildlab.com --json
```

## Tips

- DMs opened via `conversations.open` are private between those users. Group DMs (mpim) are created when 3+ users are passed.
- The channel ID returned persists -- you can cache it and reuse it for future messages.
- Prefer user IDs over emails for speed (no extra API call needed).
- Always confirm the right profile is active before DMing: `slack-cli config show`.
