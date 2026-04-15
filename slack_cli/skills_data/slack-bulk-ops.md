---
name: slack-bulk-ops
description: "Bulk Slack operations: invite multiple users to channels, bulk archive stale channels, bulk set topics. Always shows a dry-run plan before executing."
command_name: slack-cli
tags: [bulk, invite, archive, topic, batch, operations]
---
<!-- installed by slack-cli -->

# /slack-bulk-ops -- Bulk Slack Operations

Run safe bulk operations across Slack channels with mandatory dry-run-first behavior.

## Supported Operations

- **Bulk invite** -- invite a list of users to one or more channels
- **Bulk archive** -- archive channels matching criteria (stale, empty, name pattern)
- **Bulk set topic** -- set/update topics on multiple channels at once
- **Bulk set purpose** -- set/update purpose on multiple channels at once
- **Bulk kick** -- remove a user from multiple channels
- **Clone members** -- copy all members from one channel to another
- **Invite all** -- invite ALL workspace members to a channel
- **Export members** -- export member list as CSV/JSON/markdown
- **Diff channels** -- compare membership of two channels
- **Pick random** -- choose a random non-bot member from a channel
- **Find inactive** -- list members who haven't posted in N days

## Procedure

### 1. Gather the target set

Use `--json` on all discovery commands so you can parse the output programmatically.

**List all channels:**
```bash
slack-cli conversations list --json
```

**Get details for a specific channel (topic, purpose, member count, last activity):**
```bash
slack-cli conversations info CHANNEL_ID --json
```

**List members of a channel:**
```bash
slack-cli conversations members CHANNEL_ID --json
```

**Look up users by email (to resolve names to IDs):**
```bash
slack-cli users lookup someone@example.com --json
```

**List all users:**
```bash
slack-cli users list --json
```

### 2. Build a dry-run plan

Before executing ANY bulk operation, always present a plan like this:

```
## Dry Run: Bulk Invite

Users to invite:
  - U07MBKFRLAG (Tyler Fisk)
  - U07M6QW8DML (Sara Davison)

Target channels:
  1. #project-alpha (C0123ABC) -- Tyler already a member, Sara NOT a member
  2. #project-beta (C0456DEF) -- neither is a member

Actions to take:
  - Invite Sara to #project-alpha
  - Invite Tyler + Sara to #project-beta

Skipping:
  - Tyler in #project-alpha (already a member)

Total API calls: 3

Type CONFIRM to proceed, or ABORT to cancel.
```

### 3. Execute in batches

After explicit confirmation, execute in small batches with progress reporting.

**Invite users to a channel:**
```bash
slack-cli conversations invite CHANNEL_ID USER_ID1,USER_ID2
```

**Archive a channel:**
```bash
slack-cli conversations archive CHANNEL_ID
```

**Set a channel topic:**
```bash
slack-cli conversations topic CHANNEL_ID "New topic text"
```

**Set a channel purpose:**
```bash
slack-cli conversations purpose CHANNEL_ID "New purpose text"
```

**Remove a user from a channel:**
```bash
slack-cli conversations kick CHANNEL_ID USER_ID
```

Print progress as you go:
```
[1/5] Inviting U07M6QW8DML to #project-alpha (C0123ABC)... ok
[2/5] Inviting U07MBKFRLAG to #project-beta (C0456DEF)... ok
[3/5] Inviting U07M6QW8DML to #project-beta (C0456DEF)... ok
[4/5] Setting topic on #project-alpha... ok
[5/5] Setting topic on #project-beta... ok
```

On error, STOP immediately. Report what failed and ask whether to retry, skip, or abort.

### 4. Report results

```
## Results

Total:     5
Succeeded: 5
Failed:    0
Skipped:   1 (already_in_channel)
```

## Worked Examples

### Example 1: Invite 3 users to 2 channels

User asks: "Add Tyler, Sara, and Wade to #ops and #alerts"

1. Resolve names to user IDs:
   ```bash
   slack-cli users list --json
   ```
2. Get current membership of both channels:
   ```bash
   slack-cli conversations members C_OPS_ID --json
   slack-cli conversations members C_ALERTS_ID --json
   ```
3. Diff to find who is NOT already in each channel
4. Present dry-run plan
5. On CONFIRM, loop through invites:
   ```bash
   slack-cli conversations invite C_OPS_ID U_TYLER,U_SARA,U_WADE
   slack-cli conversations invite C_ALERTS_ID U_TYLER,U_SARA,U_WADE
   ```

### Example 2: Archive all channels with no messages in 90 days

1. List all channels:
   ```bash
   slack-cli conversations list --json
   ```
2. For each channel, pull recent history:
   ```bash
   slack-cli conversations history CHANNEL_ID --limit 1 --json
   ```
3. If the most recent message timestamp is older than 90 days, flag for archival
4. Present the dry-run plan (sorted by last activity, oldest first)
5. On CONFIRM, archive in batches:
   ```bash
   slack-cli conversations archive CHANNEL_ID
   ```

### Example 3: Set a standard topic on all project channels

1. List channels, filter names matching `project-*`
2. Get current topics via `conversations info`
3. Show which channels will be updated vs. already have the correct topic
4. On CONFIRM:
   ```bash
   slack-cli conversations topic C0123ABC "Status: Active | Lead: @tyler | Wiki: https://..."
   slack-cli conversations topic C0456DEF "Status: Active | Lead: @tyler | Wiki: https://..."
   ```

## New Bulk Commands (v0.2.0)

### Clone members from one channel to another

```bash
# Dry run first
slack-cli conversations clone-members --from C0123ABC --to C0456DEF --dry-run

# Execute
slack-cli conversations clone-members --from C0123ABC --to C0456DEF
```

### Invite ALL workspace members to a channel

```bash
# Dry run to see who would be invited
slack-cli conversations invite-all C0XXXXXXXXX --dry-run

# Execute
slack-cli conversations invite-all C0XXXXXXXXX
```

### Export channel member list

```bash
# Table format (default)
slack-cli conversations export-members C0XXXXXXXXX

# CSV format
slack-cli conversations export-members C0XXXXXXXXX --format csv > members.csv

# Markdown format
slack-cli conversations export-members C0XXXXXXXXX --format markdown

# JSON
slack-cli conversations export-members C0XXXXXXXXX --json
```

### Compare membership of two channels

```bash
slack-cli conversations diff C0AAAAAAA C0BBBBBBB
```

Output shows: who's only in A, only in B, and in both.

### Pick a random member from a channel

```bash
# Returns one random non-bot member
slack-cli conversations random C0XXXXXXXXX
```

### Find inactive members (haven't posted in N days)

```bash
# Default: 30 days
slack-cli conversations inactive C0XXXXXXXXX

# Custom threshold
slack-cli conversations inactive C0XXXXXXXXX --days 60

# JSON for scripting
slack-cli conversations inactive C0XXXXXXXXX --days 30 --json
```

## Safety Rules

- **Mandatory dry-run.** Never skip the plan step. Even for "just 2 channels."
- **Check membership before inviting.** Slack returns `already_in_channel` errors if you invite someone who is already a member. Pre-filter to avoid noisy error output.
- **Archive is reversible** (via `slack-cli conversations unarchive`), but always confirm before doing it.
- **Kick is sensitive.** Double-confirm before bulk kicks: "You are about to remove USER from N channels. Are you sure?"
- **Rate limiting.** Slack Tier 2 methods (invite, archive, topic) allow ~20 requests per minute. For large batches (50+ channels), add a short pause between calls.
- **Never bulk-operate without explicit profile selection.** If the user has multiple profiles, confirm which workspace before executing.
- **invite-all is a heavy operation.** It calls users.list to get all workspace members, then invites in batches. Use dry-run first to estimate the scope.

## Tips

- Use `slack-cli conversations list --json | jq` patterns for filtering channels by name, type, or member count before building the plan
- The `conversations invite` command accepts comma-separated user IDs, so you can invite up to 30 users in a single call (Slack API limit)
- For "stale channel" detection, also check if the channel has 0 or 1 members as an additional signal
- If the user says "archive everything except #general", make sure to explicitly exclude protected channels in the plan
- Use `conversations diff` to audit channel membership before bulk operations
