---
name: slack-reminders
description: "Create and manage Slack reminders. Add, list, complete, and delete reminders for any user with natural language or Unix timestamps. NOT scheduled messages (/slack-schedule). Use when setting a Slack reminder."
command_name: slack-cli
tags: [slack, reminders, time, schedule, tasks]
---
<!-- installed by slack-cli -->

# /slack-reminders -- Reminder Management

Create and manage Slack reminders for yourself or any workspace member.

## Arguments

- `/slack-reminders add <text> <time>` -- Create a reminder
- `/slack-reminders list` -- List all reminders

## Required Scope

Bot token needs: `reminders:write` (add/complete/delete), `reminders:read` (list/info)

## Procedure

### Step 1: Create a reminder

```bash
# Natural language time
slack-cli reminders add "Review the PR" "in 30 minutes"

# Specific time (natural language)
slack-cli reminders add "Send the weekly report" "tomorrow at 9am"

# Unix timestamp
slack-cli reminders add "Team standup" 1712400000

# For a specific user
slack-cli reminders add "Submit expense report" "Friday at 3pm" --user U07MBKFRLAG
```

### Step 2: List reminders

```bash
slack-cli reminders list

# JSON for scripting
slack-cli reminders list --json
```

### Step 3: Get reminder details

```bash
slack-cli reminders info Rm0XXXXXXXXX
```

### Step 4: Mark complete

```bash
slack-cli reminders complete Rm0XXXXXXXXX
```

### Step 5: Delete a reminder

```bash
slack-cli reminders delete Rm0XXXXXXXXX
```

## Computing Unix Timestamps

```bash
# macOS: 30 minutes from now
date -v+30M "+%s"

# macOS: specific date and time
date -j -f "%Y-%m-%d %H:%M" "2026-04-14 09:00" "+%s"

# Linux: 30 minutes from now
date -d "+30 minutes" "+%s"
```

## Worked Examples

### Remind Tyler to review a PR in 1 hour

```bash
slack-cli reminders add "Review PR #42 in github.com/8Dvibes/slack-toolkit" "in 1 hour" --user U07MBKFRLAG --json
```

### Create a daily reminder for yourself

```bash
# Remind yourself every weekday morning (use the time string Slack supports)
slack-cli reminders add "Morning brief check" "every weekday at 8am"
```

### Clean up old completed reminders

```bash
# List all reminders as JSON and filter for completed ones
slack-cli reminders list --json | python3 -c "
import json, sys
reminders = json.load(sys.stdin)
done = [r for r in reminders if r.get('complete_ts')]
print(f'Completed: {len(done)}')
for r in done:
    print(f\"  {r['id']}: {r['text']}\")
"
```

## Tips

- Reminder IDs start with `Rm` (e.g. `Rm0XXXXXXXXX`).
- Time strings Slack understands: "in 30 minutes", "tomorrow at 9am", "next Monday at 2pm", "every day at 8am".
- Creating reminders for other users requires the `reminders:write:user` scope.
- Completed reminders still appear in the list -- use the `complete_ts` field to filter.
