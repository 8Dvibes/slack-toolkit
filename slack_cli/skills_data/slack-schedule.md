---
name: slack-schedule
description: "Schedule Slack messages for future delivery. Convert human-readable times to Unix timestamps, list pending scheduled messages, cancel scheduled messages."
command_name: slack-cli
tags: [slack, schedule, message, timer, delay]
---
<!-- installed by slack-cli -->

# /slack-schedule -- Schedule Messages for Future Delivery

Schedule messages to be posted at a specific time, list pending scheduled messages, and cancel them before they send.

## When to Use

- Scheduling a message to post at a specific time (morning announcements, reminders)
- Queuing up messages to send during business hours
- Listing all pending scheduled messages to audit what is queued
- Canceling a scheduled message before it fires

## Procedure

### Step 1: Convert the Target Time to a Unix Timestamp

The `slack-cli chat schedule` command requires a Unix timestamp (seconds since epoch). Convert your target time:

**macOS:**

```bash
date -j -f "%Y-%m-%d %H:%M:%S" "2026-04-11 09:00:00" "+%s"
# Output: 1775991600
```

**Linux:**

```bash
date -d "2026-04-11 09:00:00" "+%s"
```

**Python (one-liner):**

```bash
python3 -c "from datetime import datetime; print(int(datetime(2026, 4, 11, 9, 0, 0).timestamp()))"
```

**Python with timezone awareness (recommended):**

```python
from datetime import datetime
from zoneinfo import ZoneInfo

# Schedule for 9 AM Central
dt = datetime(2026, 4, 11, 9, 0, 0, tzinfo=ZoneInfo("America/Chicago"))
print(int(dt.timestamp()))
```

**Important:** The Unix timestamp must be in the future and at least 1 second from now. Slack rejects timestamps in the past.

### Step 2: Schedule the Message

```bash
slack-cli chat schedule <CHANNEL_ID> "Good morning! Here is today's standup thread." <UNIX_TIMESTAMP>
```

Full example:

```bash
slack-cli chat schedule C0AM2BVMHRT "Good morning! Here is today's standup thread." 1775991600
```

The command returns a `scheduled_message_id` which you need to cancel the message later.

### Step 3: Schedule with Block Kit

```bash
slack-cli chat schedule C0AM2BVMHRT "Weekly update" 1775991600 --blocks '[{"type":"section","text":{"type":"mrkdwn","text":"*Weekly Update - April 11*\n\n- Revenue: $142K\n- Active students: 1,154\n- New enrollments: 23"}}]'
```

### Step 4: Schedule a Threaded Reply

```bash
slack-cli chat schedule C0AM2BVMHRT "Follow-up: results are in" 1775991600 --thread-ts 1712345678.123456
```

### Step 5: Capture the Scheduled Message ID

Use `--json` to get the full response including the ID:

```bash
slack-cli chat schedule C0AM2BVMHRT "Reminder: deploy at 2 PM" 1775991600 --json
```

Response includes:

```json
{
  "ok": true,
  "channel": "C0AM2BVMHRT",
  "scheduled_message_id": "Q1234567890",
  "post_at": 1775991600
}
```

Save `scheduled_message_id` if you might need to cancel it.

## Managing Scheduled Messages

### List All Pending Scheduled Messages

```bash
slack-cli chat schedule-list
```

Filter by channel:

```bash
slack-cli chat schedule-list --channel C0AM2BVMHRT
```

JSON output for programmatic use:

```bash
slack-cli chat schedule-list --json
```

The output shows: scheduled message ID, channel ID, `post_at` timestamp, and a preview of the text.

### Cancel a Scheduled Message

Before the message fires, you can cancel it:

```bash
slack-cli chat schedule-delete <CHANNEL_ID> <SCHEDULED_MESSAGE_ID>
```

Example:

```bash
slack-cli chat schedule-delete C0AM2BVMHRT Q1234567890
```

You need both the channel ID and the scheduled message ID. Get the ID from `schedule-list` if you do not have it.

## Examples

### Schedule a morning standup prompt for 9 AM CST tomorrow

```bash
# Calculate tomorrow at 9 AM CST
TOMORROW_9AM=$(python3 -c "
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
tomorrow = datetime.now(ZoneInfo('America/Chicago')).replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
print(int(tomorrow.timestamp()))
")

slack-cli chat schedule C0AM2BVMHRT "Good morning! Drop your standup updates in this thread." $TOMORROW_9AM
```

### Schedule a reminder 2 hours from now

```bash
POST_AT=$(python3 -c "import time; print(int(time.time()) + 7200)")

slack-cli chat schedule C0AM2BVMHRT "Reminder: PR review deadline in 1 hour" $POST_AT
```

### Audit and clean up scheduled messages

```bash
# List everything pending
slack-cli chat schedule-list --json

# Cancel a specific one
slack-cli chat schedule-delete C0AM2BVMHRT Q1234567890

# Verify it is gone
slack-cli chat schedule-list --channel C0AM2BVMHRT
```

### Schedule to multiple channels

```bash
POST_AT=1775991600

slack-cli chat schedule C0AM2BVMHRT "Release v2.1 is live!" $POST_AT
slack-cli chat schedule C0AGH7UG2UU "Release v2.1 is live!" $POST_AT
```

## Common Time Calculations

| Target | Shell (macOS) | Python |
|--------|--------------|--------|
| In 30 minutes | `$(($(date +%s) + 1800))` | `int(time.time()) + 1800` |
| In 1 hour | `$(($(date +%s) + 3600))` | `int(time.time()) + 3600` |
| In 24 hours | `$(($(date +%s) + 86400))` | `int(time.time()) + 86400` |
| Tomorrow 9 AM CST | See example above | Use `zoneinfo` |
| Next Monday 8 AM | Use `date -j` with calculation | Use `datetime` + `timedelta` |

## Tips

- Slack requires the scheduled time to be **at least 1 second in the future** and **no more than 120 days out**.
- The `post_at` argument to `slack-cli chat schedule` is a positional argument (not a flag). It comes after the text: `slack-cli chat schedule <channel> <text> <unix_ts>`.
- Scheduled messages are sent by the **bot**, not on behalf of a user. They appear as bot messages.
- Once a scheduled message fires, it becomes a regular message. You can no longer cancel it -- only delete it with `slack-cli chat delete`.
- If the bot loses access to the channel before the scheduled time, the message silently fails to send.
- The `schedule-list` command shows ALL scheduled messages for the bot across all channels (unless filtered with `--channel`).
- To schedule messages on a different workspace, use `--profile <name>`.
- Timezone matters. Always convert to the correct timezone before generating the Unix timestamp. When in doubt, use `America/Chicago` (CST/CDT) for this workspace.
