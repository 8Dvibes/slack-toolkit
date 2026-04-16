---
name: slack-integration-patterns
description: "Common agent-to-Slack architectural patterns with complete command sequences. Covers notification pipelines, approval flows, report posting, channel provisioning, monitoring loops, and cross-channel coordination. Use when designing how an agent or automation should interact with Slack."
command_name: slack-cli
tags: [slack, patterns, architecture, integration, automation, workflows, agents, pipelines]
---
<!-- installed by slack-cli -->

# /slack-integration-patterns -- Agent-to-Slack Architectural Patterns

Six proven patterns for how AI agents and automations should interact with Slack. Each includes a complete command sequence you can execute directly.

---

## Pattern 1: Notification Pipeline

**When to use:** Agent does work, then posts a summary to a channel.

**Structure:**
```
Agent executes task
  → Formats result as Block Kit message
  → Posts to target channel
  → Optionally pins important results
```

**Complete sequence:**

```bash
# 1. Agent does work (example: checks API health)
RESULT=$(curl -s https://api.example.com/health)
STATUS=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('healthy' if d.get('ok') else 'degraded')")

# 2. Build the message
BLOCKS=$(cat << 'EOF'
[
  {"type": "header", "text": {"type": "plain_text", "text": "Health Check Complete"}},
  {"type": "section", "fields": [
    {"type": "mrkdwn", "text": "*Status*\nhealthy"},
    {"type": "mrkdwn", "text": "*Checked*\n9:00 AM CST"}
  ]}
]
EOF
)

# 3. Post to ops channel
TS=$(slack-cli chat post C0AM2BVMHRT "Health check: $STATUS" --blocks "$BLOCKS" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['ts'])")

# 4. Save timestamp for follow-up threading
echo "$TS" > /tmp/last-health-ts.txt
```

**Key points:**
- Always capture the returned `ts` (timestamp) if you may need to thread replies or update the message
- Use `--json` to get the full response with `ts`
- Prefer channel IDs over channel names for reliability

---

## Pattern 2: Approval Flow

**When to use:** Agent drafts an action, requests human approval in Slack, waits for a signal, then executes.

**Structure:**
```
Agent drafts action
  → Posts to ops channel with approval request
  → Polls for a reaction (or message reply) as approval signal
  → Executes action (or aborts) based on signal
```

**Complete sequence:**

```bash
# 1. Post approval request
TS=$(slack-cli chat post C0AM2BVMHRT "Approval needed: deploy v2.4.1 to production" --blocks '[
  {"type": "header", "text": {"type": "plain_text", "text": "Action Required: Deploy Approval"}},
  {"type": "section", "text": {"type": "mrkdwn", "text": "*Action:* Deploy v2.4.1 to production\n*Impact:* 5-min window\n*Risk:* Low"}},
  {"type": "section", "text": {"type": "mrkdwn", "text": "React :white_check_mark: to approve or :x: to reject."}}
]' --json | python3 -c "import sys,json; print(json.load(sys.stdin)['ts'])")

echo "Approval request posted. Waiting... (ts: $TS)"

# 2. Poll for reaction (check every 30 seconds for up to 10 minutes)
CHANNEL="C0AM2BVMHRT"
APPROVED=""
for i in $(seq 1 20); do
  sleep 30
  REACTIONS=$(slack-cli api reactions.get --params "{\"channel\": \"$CHANNEL\", \"timestamp\": \"$TS\"}" --json \
    | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('message',{}).get('reactions',[]); print(','.join(x['name'] for x in r))" 2>/dev/null)

  if echo "$REACTIONS" | grep -q "white_check_mark"; then
    APPROVED="yes"
    break
  elif echo "$REACTIONS" | grep -q "^x$"; then
    APPROVED="no"
    break
  fi
done

# 3. Act on approval signal
if [ "$APPROVED" = "yes" ]; then
  slack-cli chat post "$CHANNEL" "Approved. Starting deploy..." --thread-ts "$TS"
  # ... execute deploy ...
elif [ "$APPROVED" = "no" ]; then
  slack-cli chat post "$CHANNEL" "Deploy rejected. Aborting." --thread-ts "$TS"
else
  slack-cli chat post "$CHANNEL" "Approval timed out after 10 minutes. Aborting." --thread-ts "$TS"
fi
```

**Key points:**
- Thread all follow-up messages back to the original approval message using `--thread-ts`
- Use distinct emoji for approve/reject to avoid ambiguity
- Always handle the timeout case

---

## Pattern 3: Report Posting

**When to use:** Agent generates data, formats it as a rich Block Kit message, and optionally attaches a file.

**Structure:**
```
Agent generates data
  → Formats as Block Kit message with field sections
  → Posts to channel
  → Uploads supporting file (CSV, JSON, etc.) as thread reply
```

**Complete sequence:**

```bash
# 1. Generate report data (example: credit usage summary)
REPORT_JSON=$(python3 << 'EOF'
import json
data = {
    "total_students": 1154,
    "credits_used": 5400000,
    "credits_remaining": 601000,
    "high_usage_count": 23,
    "blocked_count": 0
}
print(json.dumps(data))
EOF
)

TOTAL=$(echo "$REPORT_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['total_students'])")
USED=$(echo "$REPORT_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['credits_used']:,}\")")
BLOCKED=$(echo "$REPORT_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['blocked_count'])")

# 2. Post Block Kit report
TS=$(slack-cli chat post C0AM2BVMHRT "Credit ops report" --blocks "[
  {\"type\": \"header\", \"text\": {\"type\": \"plain_text\", \"text\": \"Credit Ops Report\"}},
  {\"type\": \"section\", \"fields\": [
    {\"type\": \"mrkdwn\", \"text\": \"*Students*\n$TOTAL\"},
    {\"type\": \"mrkdwn\", \"text\": \"*Credits Used*\n$USED\"},
    {\"type\": \"mrkdwn\", \"text\": \"*High Usage*\n23\"},
    {\"type\": \"mrkdwn\", \"text\": \"*Blocked*\n$BLOCKED\"}
  ]},
  {\"type\": \"context\", \"elements\": [{\"type\": \"mrkdwn\", \"text\": \"Generated by Gigawatt | $(date '+%I:%M %p CST')\"}]}
]" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['ts'])")

# 3. Upload supporting CSV as thread reply
echo "$REPORT_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print('metric,value'); [print(f'{k},{v}') for k,v in d.items()]" > /tmp/report.csv
slack-cli files upload C0AM2BVMHRT /tmp/report.csv --title "credit-ops-detail.csv" --thread-ts "$TS"
```

---

## Pattern 4: Channel Provisioning

**When to use:** Agent creates a new Slack channel with a full setup: topic, members, welcome message.

**Structure:**
```
Create channel
  → Set topic and purpose
  → Invite members
  → Add bookmarks
  → Post welcome message
```

**Complete sequence:**

```bash
CHANNEL_NAME="project-atlas-ops"
MEMBER_IDS="U07MBKFRLAG,U07M6QW8DML"  # Tyler, Sara

# 1. Create channel
CHANNEL_ID=$(slack-cli conversations create "$CHANNEL_NAME" --json \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['channel']['id'])")

echo "Created channel: $CHANNEL_ID"

# 2. Set purpose and topic
slack-cli api conversations.setPurpose \
  --params "{\"channel\": \"$CHANNEL_ID\", \"purpose\": \"Operations coordination for Project Atlas\"}"

slack-cli api conversations.setTopic \
  --params "{\"channel\": \"$CHANNEL_ID\", \"topic\": \"Project Atlas | Sprint 1 (Apr 14 - Apr 28)\"}"

# 3. Invite members
for uid in $(echo "$MEMBER_IDS" | tr ',' ' '); do
  slack-cli conversations invite "$CHANNEL_ID" "$uid"
done

# 4. Add a bookmark (link to project docs)
slack-cli api bookmarks.add \
  --params "{\"channel_id\": \"$CHANNEL_ID\", \"title\": \"Project Docs\", \"type\": \"link\", \"link\": \"https://notion.so/project-atlas\"}"

# 5. Post welcome message
slack-cli chat post "$CHANNEL_ID" "Channel ready" --blocks '[
  {"type": "header", "text": {"type": "plain_text", "text": "Welcome to #project-atlas-ops"}},
  {"type": "section", "text": {"type": "mrkdwn", "text": "This channel is for operational coordination on Project Atlas.\n\n*Sprint 1:* April 14 - April 28\n*Standup:* Daily 9 AM CST"}},
  {"type": "context", "elements": [{"type": "mrkdwn", "text": "Channel provisioned automatically by Gigawatt"}]}
]'
```

---

## Pattern 5: Monitoring Loop

**When to use:** Agent polls a Slack channel for new messages, processes them, and responds in thread.

**Structure:**
```
Get latest ts cursor
  → Poll for new messages since cursor
  → Filter/process messages
  → Respond in thread
  → Advance cursor
```

**Complete sequence:**

```bash
CHANNEL="C0AM2BVMHRT"
CURSOR_FILE="/tmp/slack-monitor-cursor.txt"

# Initialize cursor (start from now)
if [ ! -f "$CURSOR_FILE" ]; then
  slack-cli api conversations.history \
    --params "{\"channel\": \"$CHANNEL\", \"limit\": 1}" --json \
    | python3 -c "import sys,json; msgs=json.load(sys.stdin).get('messages',[]); print(msgs[0]['ts'] if msgs else '')" \
    > "$CURSOR_FILE"
fi

# Poll loop
while true; do
  SINCE=$(cat "$CURSOR_FILE")

  MESSAGES=$(slack-cli api conversations.history \
    --params "{\"channel\": \"$CHANNEL\", \"oldest\": \"$SINCE\", \"limit\": 50}" \
    --json)

  # Process each message
  echo "$MESSAGES" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
for msg in reversed(data.get("messages", [])):
    if msg.get("subtype"):  # Skip system messages
        continue
    text = msg.get("text", "")
    ts = msg.get("ts", "")
    user = msg.get("user", "")
    # Filter: only process messages mentioning "deploy"
    if "deploy" in text.lower():
        print(f"PROCESS: {user} at {ts}: {text[:100]}")
PYEOF

  # Update cursor to latest ts seen
  NEW_CURSOR=$(echo "$MESSAGES" | python3 -c \
    "import sys,json; msgs=json.load(sys.stdin).get('messages',[]); print(msgs[0]['ts'] if msgs else '')" 2>/dev/null)

  if [ -n "$NEW_CURSOR" ]; then
    echo "$NEW_CURSOR" > "$CURSOR_FILE"
  fi

  sleep 60  # Poll every 60 seconds
done
```

**Key points:**
- Store the cursor between runs to avoid reprocessing messages
- Skip messages with `subtype` (system messages: joins, leaves, topic changes)
- Respond in thread using `--thread-ts MESSAGE_TS`
- Be careful of `chat.postMessage` rate limit (1/second per channel)

---

## Pattern 6: Cross-Channel Coordination

**When to use:** Agent reads from one channel (source of truth), synthesizes, and posts to another (distribution channel).

**Structure:**
```
Read messages from source channel(s)
  → Filter/aggregate relevant content
  → Format as summary
  → Post to distribution channel
```

**Complete sequence:**

```bash
# Read from source channel (e.g., ops channel)
OPS_HISTORY=$(slack-cli api conversations.history \
  --params '{"channel": "C0AM2BVMHRT", "limit": 100, "oldest": "'"$(date -v-24H '+%s')"'"}' \
  --json)

# Count and extract key signals
MESSAGE_COUNT=$(echo "$OPS_HISTORY" | python3 -c \
  "import sys,json; msgs=json.load(sys.stdin).get('messages',[]); print(len([m for m in msgs if not m.get('subtype')]))")

ALERTS=$(echo "$OPS_HISTORY" | python3 << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
alerts = []
for msg in data.get("messages", []):
    text = msg.get("text", "").lower()
    if any(kw in text for kw in ["error", "failed", "alert", "warning"]):
        alerts.append(msg.get("text", "")[:80])
print("\n".join(f"- {a}" for a in alerts[:5]) if alerts else "None")
PYEOF
)

# Post digest to distribution channel
slack-cli chat post C0AGH7UG2UU "Daily digest from ops" --blocks "[
  {\"type\": \"header\", \"text\": {\"type\": \"plain_text\", \"text\": \"Gigawatt Lounge Digest\"}},
  {\"type\": \"section\", \"fields\": [
    {\"type\": \"mrkdwn\", \"text\": \"*Messages (24h)*\n$MESSAGE_COUNT\"},
    {\"type\": \"mrkdwn\", \"text\": \"*Source*\n<#C0AM2BVMHRT>\"}
  ]},
  {\"type\": \"divider\"},
  {\"type\": \"section\", \"text\": {\"type\": \"mrkdwn\", \"text\": \"*Alerts Detected:*\n$ALERTS\"}},
  {\"type\": \"context\", \"elements\": [{\"type\": \"mrkdwn\", \"text\": \"Digest posted by Gigawatt | $(date '+%I:%M %p CST')\"}]}
]"
```

---

## Choosing the Right Pattern

| Situation | Pattern |
|-----------|---------|
| Agent finishes a job and wants to report | Notification Pipeline |
| Agent needs human sign-off before acting | Approval Flow |
| Agent generates a data report | Report Posting |
| Setting up a new project workspace | Channel Provisioning |
| Agent watches a channel for triggers | Monitoring Loop |
| Agent reads one channel to update another | Cross-Channel Coordination |

---

## Common Mistakes

- **Not capturing the `ts` return value.** If you may need to thread, update, or react to a message, always capture `ts` from the `--json` response immediately after posting.
- **Using channel names instead of IDs.** Names can change; IDs are permanent. Use IDs in all scripts.
- **Not handling the monitoring loop cursor.** Without a persistent cursor, you reprocess all messages on every run.
- **Posting the full message as fallback text.** The fallback text should be a short notification summary, not the full Block Kit content repeated.
- **Rate limit violations in approval polling.** `reactions.get` is Tier 3 (50/min). Polling every 30 seconds is fine; polling every second will hit limits.
