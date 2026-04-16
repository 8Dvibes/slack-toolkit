---
name: slack-assistant
description: "Manage Slack AI assistant thread metadata. Set processing status, suggested prompts, and thread titles via assistant.threads API. Use when building or maintaining a Slack AI assistant integration."
command_name: slack-cli
tags: [slack, assistant, ai, threads, prompts]
---
<!-- installed by slack-cli -->

# /slack-assistant -- Slack AI Assistant Thread Management

Manage Slack AI assistant thread metadata: status, suggested prompts, and titles.

## Required Scope

Bot token needs: `assistant:write`

## API Methods Used (via slack-cli api passthrough)

- `assistant.threads.setStatus` -- Set the processing status
- `assistant.threads.setSuggestedPrompts` -- Set suggested follow-up prompts
- `assistant.threads.setTitle` -- Set the thread title
- `assistant.search.context` -- Get search context for a thread
- `assistant.search.info` -- Get search info for a thread

## Procedure

### Step 1: Set thread status while processing

Call this while your assistant is working to show a "thinking" indicator:

```bash
slack-cli api assistant.threads.setStatus --params '{
  "channel_id": "D0XXXXXXXXX",
  "thread_ts": "1712345678.000100",
  "status": "Searching knowledge base..."
}'
```

Clear the status when done (empty string):

```bash
slack-cli api assistant.threads.setStatus --params '{
  "channel_id": "D0XXXXXXXXX",
  "thread_ts": "1712345678.000100",
  "status": ""
}'
```

### Step 2: Set a thread title

```bash
slack-cli api assistant.threads.setTitle --params '{
  "channel_id": "D0XXXXXXXXX",
  "thread_ts": "1712345678.000100",
  "title": "Question about Q1 revenue"
}'
```

### Step 3: Set suggested prompts

After responding, offer the user follow-up options:

```bash
slack-cli api assistant.threads.setSuggestedPrompts --params '{
  "channel_id": "D0XXXXXXXXX",
  "thread_ts": "1712345678.000100",
  "prompts": [
    {"title": "Show me the chart", "message": "Can you create a chart of this data?"},
    {"title": "Compare to last quarter", "message": "How does this compare to Q4?"},
    {"title": "Export as CSV", "message": "Export this as a CSV file"}
  ]
}'
```

### Step 4: Get search context

When a user asks something that might benefit from search:

```bash
slack-cli api assistant.search.context --params '{
  "channel_id": "D0XXXXXXXXX",
  "thread_ts": "1712345678.000100"
}'
```

## Full Assistant Response Flow

```bash
#!/bin/bash
CHANNEL="D0XXXXXXXXX"
THREAD_TS="1712345678.000100"

# 1. Acknowledge and show status
slack-cli api assistant.threads.setStatus --params "{
  \"channel_id\": \"$CHANNEL\",
  \"thread_ts\": \"$THREAD_TS\",
  \"status\": \"Thinking...\"
}"

# 2. Set a descriptive title
slack-cli api assistant.threads.setTitle --params "{
  \"channel_id\": \"$CHANNEL\",
  \"thread_ts\": \"$THREAD_TS\",
  \"title\": \"Revenue Analysis Request\"
}"

# 3. Do your processing here...

# 4. Post the response
slack-cli chat post "$CHANNEL" "Here's the analysis: ..." --thread-ts "$THREAD_TS"

# 5. Clear status
slack-cli api assistant.threads.setStatus --params "{
  \"channel_id\": \"$CHANNEL\",
  \"thread_ts\": \"$THREAD_TS\",
  \"status\": \"\"
}"

# 6. Offer follow-up prompts
slack-cli api assistant.threads.setSuggestedPrompts --params "{
  \"channel_id\": \"$CHANNEL\",
  \"thread_ts\": \"$THREAD_TS\",
  \"prompts\": [{\"title\": \"More details\", \"message\": \"Tell me more\"}]
}"
```

## Tips

- Set status immediately when you receive a message -- users expect instant feedback.
- Keep status text short and action-oriented ("Searching...", "Analyzing data...", "Writing response...").
- Suggested prompts appear below your response and make it easy for users to continue the conversation.
- Thread titles appear in the assistant sidebar for easy navigation.
