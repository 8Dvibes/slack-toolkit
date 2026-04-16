---
name: slack-streaming
description: "Stream text into Slack in real time. Uses chat.startStream/appendStream/stopStream API via passthrough. Use when posting AI-generated responses that should appear progressively, not all at once."
command_name: slack-cli
tags: [slack, streaming, ai, chat, stream, realtime]
---
<!-- installed by slack-cli -->

# /slack-streaming -- AI Response Streaming

Stream AI-generated text into Slack channels in real-time using the streaming API.

## Required Scope

Bot token needs: `chat:write`

## API Methods Used

- `chat.startStream` -- Initialize a streaming message
- `chat.appendStream` -- Append chunks to the stream
- `chat.stopStream` -- Finalize the streaming message

All three are called via `slack-cli api` passthrough.

## Procedure

### Step 1: Start a stream

```bash
STREAM=$(slack-cli api chat.startStream --params '{
  "channel": "C08ACMRDC04",
  "initial_message": "Generating response..."
}' --json)

# Extract the stream_ts and channel
STREAM_TS=$(echo "$STREAM" | python3 -c "import json,sys; print(json.load(sys.stdin)['ts'])")
```

### Step 2: Append chunks as they arrive

```bash
# Append text chunks (call this repeatedly as you generate content)
slack-cli api chat.appendStream --params "{
  \"channel\": \"C08ACMRDC04\",
  \"ts\": \"$STREAM_TS\",
  \"text\": \"Here is the first part of the response...\"
}"

# Continue appending
slack-cli api chat.appendStream --params "{
  \"channel\": \"C08ACMRDC04\",
  \"ts\": \"$STREAM_TS\",
  \"text\": \"And here is more content.\"
}"
```

### Step 3: Stop the stream

```bash
slack-cli api chat.stopStream --params "{
  \"channel\": \"C08ACMRDC04\",
  \"ts\": \"$STREAM_TS\"
}"
```

## Full Streaming Script Example

```bash
#!/bin/bash
CHANNEL="C08ACMRDC04"

# Start the stream
RESP=$(slack-cli api chat.startStream --params "{\"channel\":\"$CHANNEL\"}" --json)
TS=$(echo "$RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ts',''))")

if [ -z "$TS" ]; then
  echo "Failed to start stream" >&2
  exit 1
fi

# Simulate streaming AI output in chunks
chunks=("The analysis shows " "three key trends: " "1) adoption is up 40%, " "2) costs dropped 15%, " "3) quality improved.")

for chunk in "${chunks[@]}"; do
  slack-cli api chat.appendStream --params "{
    \"channel\": \"$CHANNEL\",
    \"ts\": \"$TS\",
    \"text\": \"$chunk\"
  }" > /dev/null
  sleep 0.5  # Simulate generation delay
done

# Finalize
slack-cli api chat.stopStream --params "{\"channel\":\"$CHANNEL\",\"ts\":\"$TS\"}"
echo "Done. Message ts: $TS"
```

## Threading Streams

To stream into a thread:

```bash
slack-cli api chat.startStream --params '{
  "channel": "C08ACMRDC04",
  "thread_ts": "1712345678.000100"
}'
```

## Tips

- Streaming messages appear with a "typing" indicator while the stream is open.
- Call `appendStream` frequently (every 1-3 seconds) to keep the indicator active.
- Always call `stopStream` -- orphaned streams may consume resources.
- The `ts` from `startStream` can be used later with `chat.update` to revise the final message.
- Rate limits apply: don't call `appendStream` more than once per second.
