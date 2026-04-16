---
name: slack-calls
description: "Register external voice/video calls (Zoom, Meet) in Slack's native call UI. Add, end, update, and query calls via API passthrough. Use when integrating an external call system with Slack."
command_name: slack-cli
tags: [slack, calls, video, voice, zoom, meet]
---
<!-- installed by slack-cli -->

# /slack-calls -- Voice and Video Call Registration

Register external calls (Zoom, Google Meet, etc.) in Slack's native call UI via the `slack-cli api` passthrough.

## Required Scope

Bot token needs: `calls:write` (add/end/update), `calls:read` (info)

## API Methods Used (via slack-cli api passthrough)

- `calls.add` -- Register an external call
- `calls.end` -- End/close a call
- `calls.info` -- Get call details
- `calls.update` -- Update call status
- `calls.participants.add` -- Add participants
- `calls.participants.remove` -- Remove participants

## Procedure

### Step 1: Register an external call

```bash
CALL=$(slack-cli api calls.add --params '{
  "external_unique_id": "zoom-meeting-12345",
  "join_url": "https://zoom.us/j/12345?pwd=abc",
  "title": "Team Sync",
  "desktop_app_join_url": "zoommtg://zoom.us/join?confno=12345"
}' --json)

CALL_ID=$(echo "$CALL" | python3 -c "import json,sys; print(json.load(sys.stdin)['call']['id'])")
echo "Call ID: $CALL_ID"
```

### Step 2: Share the call in a Slack channel

After registering, post a message with the call attached:

```bash
slack-cli chat post C08ACMRDC04 "Team sync starting now!" --blocks "[
  {
    \"type\": \"call\",
    \"call_id\": \"$CALL_ID\"
  }
]"
```

Or use the `calls.add` response which includes a `message` block automatically.

### Step 3: Add participants

```bash
slack-cli api calls.participants.add --params "{
  \"id\": \"$CALL_ID\",
  \"users\": [
    {\"slack_id\": \"U07MBKFRLAG\"},
    {\"slack_id\": \"U07M6QW8DML\"}
  ]
}"
```

### Step 4: Update call status

```bash
# Update with current participant count
slack-cli api calls.update --params "{
  \"id\": \"$CALL_ID\",
  \"join_url\": \"https://zoom.us/j/12345\",
  \"title\": \"Team Sync (in progress)\"
}"
```

### Step 5: Get call info

```bash
slack-cli api calls.info --params "{\"id\": \"$CALL_ID\"}" --json
```

### Step 6: End the call

```bash
slack-cli api calls.end --params "{\"id\": \"$CALL_ID\"}"
```

## Worked Example: Automated Zoom to Slack Integration

```bash
#!/bin/bash
# When a Zoom meeting starts, register it in Slack and post to the team channel

ZOOM_MEETING_ID="$1"
ZOOM_JOIN_URL="https://zoom.us/j/$ZOOM_MEETING_ID"
CHANNEL="C0AM2BVMHRT"  # Gigawatt Lounge

# Register the call
RESP=$(slack-cli api calls.add --params "{
  \"external_unique_id\": \"zoom-$ZOOM_MEETING_ID\",
  \"join_url\": \"$ZOOM_JOIN_URL\",
  \"title\": \"Team Meeting\",
  \"users\": [{\"slack_id\": \"U07MBKFRLAG\"}, {\"slack_id\": \"U07M6QW8DML\"}]
}" --json)

CALL_ID=$(echo "$RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['call']['id'])")

# Post to Slack
slack-cli chat post "$CHANNEL" "Meeting started -- join now!" --blocks "[
  {\"type\": \"call\", \"call_id\": \"$CALL_ID\"}
]"
```

## Tips

- `external_unique_id` must be unique per call session -- use meeting IDs from your call provider.
- The `calls.add` API returns a preformatted message you can post directly.
- Calls appear in Slack with a native call UI including participant count.
- Always call `calls.end` when the meeting ends to update the Slack call widget.
- `desktop_app_join_url` enables one-click joining via the native desktop app (e.g. Zoom's deep link).
