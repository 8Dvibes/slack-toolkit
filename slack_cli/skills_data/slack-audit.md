---
name: slack-audit
description: "Audit Slack workspace hygiene. Finds stale channels, missing topics, membership gaps, and permission issues. Read-only analysis only. NOT for bulk fixes (/slack-bulk-ops). Use when reviewing workspace health."
command_name: slack-cli
tags: [audit, hygiene, channels, compliance, stale, topics, members]
---
<!-- installed by slack-cli -->

# /slack-audit -- Slack Workspace Audit

Run a comprehensive read-only audit of the Slack workspace to surface hygiene issues, stale channels, missing metadata, and membership gaps.

**This skill is read-only by design.** It reports findings but never modifies anything. Use the `/slack-bulk-ops` skill to act on the findings.

## Procedure

### 1. Inventory the workspace

Run all discovery commands with `--json` for machine-parseable output.

**All channels (public + private):**
```bash
slack-cli conversations list --json
```

**Include archived channels too (for completeness):**
```bash
slack-cli conversations list --include-archived --json
```

**All users:**
```bash
slack-cli users list --json
```

### 2. Audit each channel

For every non-archived channel, gather details:

**Channel info (topic, purpose, member count, created date):**
```bash
slack-cli conversations info CHANNEL_ID --json
```

**Channel members:**
```bash
slack-cli conversations members CHANNEL_ID --json
```

**Recent message history (check for staleness):**
```bash
slack-cli conversations history CHANNEL_ID --limit 1 --json
```

### 3. Run the checks

#### Check A: Stale channels (no recent activity)

For each channel, compare the timestamp of the most recent message to now:
- **Critical (90+ days):** Flag as "stale -- candidate for archival"
- **Warning (30-90 days):** Flag as "low activity -- investigate"
- **Born dead (zero messages ever):** Flag as "empty since creation"

#### Check B: Missing topics

Look at the `topic.value` field from `conversations info`:
- Empty or whitespace-only topic = missing
- Topic that is just the default Slack text = missing

```bash
slack-cli conversations info CHANNEL_ID --json
```

Parse the JSON: if `channel.topic.value` is empty, flag it.

#### Check C: Missing purposes

Same as topics but check `channel.purpose.value`:
- Empty or default purpose = missing

#### Check D: Expected membership gaps

If the user provides an expected membership list (e.g., "Tyler and Sara should be in all project channels"), cross-reference:

1. Get the expected user IDs
2. For each target channel, pull members:
   ```bash
   slack-cli conversations members CHANNEL_ID --json
   ```
3. Report any channels where expected users are missing

#### Check E: Ghost channels (very few members)

Flag channels with 0-1 non-bot members. These are often abandoned.

#### Check F: Duplicate-looking channels

Look for channels with very similar names (e.g., `#project-foo` and `#project-foo-2`, or `#ops` and `#operations`). Flag these for human review.

### 4. Present the audit report

```
## Slack Workspace Audit -- [workspace name] -- [date]

### Summary
- Total channels: N (X public, Y private, Z archived)
- Total users: N (M active, K deactivated)
- Issues found: N

### Stale Channels (no activity in 90+ days)
| Channel | ID | Last Message | Members | Recommendation |
|---------|----|-------------|---------|----------------|
| #old-project | C0123 | 2025-11-15 | 3 | Archive |
| #test-channel | C0456 | never | 1 | Archive or delete |

### Low Activity Channels (30-90 days)
| Channel | ID | Last Message | Members |
|---------|----|-------------|---------|
| #quarterly-review | C0789 | 2026-02-10 | 8 |

### Channels Missing Topics
| Channel | ID | Members | Has Purpose? |
|---------|----|---------|-------------|
| #random-stuff | C0ABC | 12 | No |

### Channels Missing Purposes
| Channel | ID | Members | Has Topic? |
|---------|----|---------|-----------|
| #alerts | C0DEF | 5 | Yes |

### Membership Gaps (expected users not present)
| Channel | Missing Users |
|---------|--------------|
| #ops | Sara (U07M6QW8DML) |

### Ghost Channels (0-1 non-bot members)
| Channel | ID | Members |
|---------|----|---------|
| #abandoned | C0GHI | 0 |

### Recommended Next Actions
1. Archive N stale channels (use `/slack-bulk-ops`)
2. Set topics on N channels (use `/slack-bulk-ops`)
3. Invite missing users to N channels (use `/slack-bulk-ops`)
4. Investigate N low-activity channels
5. Review N duplicate-looking channel pairs
```

## Worked Examples

### Example 1: Full workspace audit

User asks: "Audit our Slack workspace"

Run the complete procedure above. For workspaces with many channels (50+), batch the `conversations info` calls and show progress:
```
Auditing channel 12/47: #design-team...
```

### Example 2: "Which channels are missing topics?"

Targeted audit -- only run Check B:
```bash
slack-cli conversations list --json
```
Then for each channel:
```bash
slack-cli conversations info CHANNEL_ID --json
```
Filter for empty `topic.value` and report.

### Example 3: "Is Tyler in all the project channels?"

Targeted membership audit:
1. Resolve Tyler's user ID:
   ```bash
   slack-cli users lookup tyler@aibuildlab.com --json
   ```
2. List channels matching `project-*`:
   ```bash
   slack-cli conversations list --json
   ```
3. For each matching channel:
   ```bash
   slack-cli conversations members CHANNEL_ID --json
   ```
4. Report any channels where Tyler's ID is not in the member list.

## Rate Limiting Notes

- `conversations.list` is Tier 2 (~20/min)
- `conversations.info` is Tier 3 (~50/min) -- safe for rapid-fire
- `conversations.history` is Tier 3 (~50/min)
- `conversations.members` is Tier 4 (~100/min) -- very generous

For a workspace with 100 channels, the full audit takes roughly 2-3 minutes due to rate limits on the info/history calls. Show progress to keep the user informed.

## Tips

- Start with `conversations list` to get the total count before diving into per-channel calls. If there are 500+ channels, ask the user if they want to audit all of them or filter by name/type first.
- The `--include-archived` flag on `conversations list` is useful for counting total archived channels but skip the per-channel audit for archived ones (they are already out of the way).
- Bot users and Slackbot show up in member lists. Filter them out when counting "real" members. Bot users have `is_bot: true` in `users list` output.
- For the "expected membership" check, ask the user to provide either email addresses or user IDs. Emails are easier for humans; use `slack-cli users lookup EMAIL` to resolve them.
