---
name: slack-dnd
description: "Manage Slack Do Not Disturb settings: check DND status, enable/disable snooze, and check team DND status."
command_name: slack-cli
tags: [slack, dnd, snooze, notifications, do-not-disturb]
---
<!-- installed by slack-cli -->

# /slack-dnd -- Do Not Disturb Management

Check and manage Slack Do Not Disturb (DND) settings for users and teams.

## Arguments

- `/slack-dnd info` -- Check DND status for a user
- `/slack-dnd snooze <minutes>` -- Enable snooze

## Required Scope

Bot token needs: `dnd:read` (info/team-info), `dnd:write` (set-snooze/end-snooze/end-dnd)

## Procedure

### Step 1: Check DND status for a user

```bash
# Check your own status (authed user)
slack-cli dnd info

# Check a specific user
slack-cli dnd info --user U07MBKFRLAG

# JSON output
slack-cli dnd info --user U07MBKFRLAG --json
```

### Step 2: Enable snooze

```bash
# Snooze for 30 minutes
slack-cli dnd set-snooze --minutes 30

# Snooze for 2 hours (120 minutes)
slack-cli dnd set-snooze --minutes 120
```

### Step 3: End snooze early

```bash
slack-cli dnd end-snooze
```

### Step 4: End a full DND session

```bash
slack-cli dnd end-dnd
```

### Step 5: Check team DND status

```bash
# Check DND for specific users
slack-cli dnd team-info --users U07MBKFRLAG,U07M6QW8DML

# JSON for scripting
slack-cli dnd team-info --users U07MBKFRLAG,U07M6QW8DML --json
```

## Worked Examples

### Check if Tyler is available before DMing

```bash
DND=$(slack-cli dnd info --user U07MBKFRLAG --json)
SNOOZE=$(echo "$DND" | python3 -c "import json,sys; print(json.load(sys.stdin).get('snooze_enabled', False))")
DND_ON=$(echo "$DND" | python3 -c "import json,sys; print(json.load(sys.stdin).get('dnd_enabled', False))")

if [ "$SNOOZE" = "True" ] || [ "$DND_ON" = "True" ]; then
  echo "Tyler has DND on -- consider waiting"
else
  echo "Tyler is available"
  slack-cli conversations open --users U07MBKFRLAG
fi
```

### Snooze during focus time

```bash
# Enable 90-minute focus block
slack-cli dnd set-snooze --minutes 90
echo "DND enabled for 90 minutes"

# ... do focused work ...

# End it early when done
slack-cli dnd end-snooze
```

### Check team availability before posting an urgent message

```bash
slack-cli dnd team-info --users U07MBKFRLAG,U07M6QW8DML,U07MV3K3203 --json | python3 -c "
import json, sys
team = json.load(sys.stdin)
unavailable = [uid for uid, info in team.items()
               if info.get('snooze_enabled') or info.get('dnd_enabled')]
print(f'Unavailable: {unavailable}')
"
```

## Tips

- DND status respects user-configured schedules (e.g. quiet hours). Check before sending non-urgent messages late at night.
- `end-dnd` ends the full DND schedule period; `end-snooze` only ends a manual snooze.
- `set-snooze` starts from the current moment and lasts the specified number of minutes.
- Team DND info works best when you have a list of specific user IDs.
