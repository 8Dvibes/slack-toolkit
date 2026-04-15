---
name: slack-usergroup
description: "Manage Slack user groups: create, list, update, enable/disable, and manage members. Use @handle mentions to address groups in messages."
command_name: slack-cli
tags: [slack, usergroup, team, group, members, @mention]
---
<!-- installed by slack-cli -->

# /slack-usergroup -- User Group Management

Create and manage Slack user groups for @handle mentions.

## Arguments

- `/slack-usergroup create <name>` -- Create a new user group
- `/slack-usergroup list` -- List all user groups

## Required Scope

`usergroups:write` (create/update/disable/enable/members), `usergroups:read` (list)

## Procedure

### Step 1: List existing user groups

```bash
slack-cli usergroups list

# Include disabled groups
slack-cli usergroups list --include-disabled

# JSON output for scripting
slack-cli usergroups list --json
```

### Step 2: Create a user group

```bash
# Basic group
slack-cli usergroups create "Engineering Team" --handle engineers

# With description and default channels
slack-cli usergroups create "Design Team" \
  --handle designers \
  --description "All product designers" \
  --channels C08ACMRDC04,C0AGH7UG2UU
```

### Step 3: Update a user group

```bash
slack-cli usergroups update S0XXXXXXXXX \
  --name "Engineering Team 2026" \
  --description "Updated description"
```

### Step 4: Manage members

```bash
# List current members
slack-cli usergroups members-list S0XXXXXXXXX

# Set members (REPLACES the entire list)
slack-cli usergroups members-update S0XXXXXXXXX \
  --users U07MBKFRLAG,U07M6QW8DML,U07MV3K3203
```

Note: `members-update` replaces the entire member list. To add one person, first get the current list and include all existing members plus the new one.

### Step 5: Enable or disable

```bash
# Disable a group (it still exists but @mention won't work)
slack-cli usergroups disable S0XXXXXXXXX

# Re-enable
slack-cli usergroups enable S0XXXXXXXXX
```

## Worked Examples

### Create @founders group and add Tyler and Sara

```bash
# Create
slack-cli usergroups create "Founders" --handle founders --json

# Get the S-prefixed ID from the response
# Set members
slack-cli usergroups members-update S0XXXXXXXXX --users U07MBKFRLAG,U07M6QW8DML
```

### Add a new member to an existing group

```bash
# Get current members
CURRENT=$(slack-cli usergroups members-list S0XXXXXXXXX --json | python3 -c "import json,sys; print(','.join(json.load(sys.stdin)))")

# Add the new member
slack-cli usergroups members-update S0XXXXXXXXX --users "$CURRENT,U_NEW_USER_ID"
```

### Audit all user groups

```bash
slack-cli usergroups list --include-disabled --json | python3 -c "
import json, sys
groups = json.load(sys.stdin)
for g in groups:
    disabled = 'DISABLED' if g.get('date_delete') else 'active'
    print(f\"{g['id']} @{g['handle']}: {g.get('user_count',0)} members ({disabled})\")
"
```

## Tips

- User group IDs start with `S` (e.g. `S0ABC123`).
- `@handle` mentions in messages will notify all group members.
- Members-update replaces the full list -- always fetch first if you want to append.
- Disabled groups retain their ID and handle, but @mentions don't send notifications.
