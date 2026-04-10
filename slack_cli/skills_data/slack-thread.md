---
name: slack-thread
description: "Read and reply to Slack threads with full context. Get thread parent + all replies, post threaded replies, follow up on conversations."
command_name: slack-cli
tags: [slack, thread, conversation, reply]
---
<!-- installed by slack-cli -->

# /slack-thread -- Read and Reply to Slack Threads

Read full thread context and post threaded replies using `slack-cli`.

## When to Use

- Reading all replies in a Slack thread
- Posting a reply to an existing thread
- Following up on a conversation someone mentioned
- Checking what was said in a thread before responding
- Building a summary of a threaded discussion

## Procedure

### Step 1: Get the Thread Context

You need two things: the **channel ID** and the **thread parent timestamp** (`thread_ts`).

If you only have a channel ID and need to find a thread, pull recent history first:

```bash
slack-cli conversations history <CHANNEL_ID> --limit 20 --json
```

Look for messages with `"reply_count"` > 0 -- those are thread parents. The `"ts"` field of the parent message is the `thread_ts` you need.

### Step 2: Read the Full Thread

```bash
slack-cli conversations replies <CHANNEL_ID> <THREAD_TS>
```

This returns the parent message plus all replies, in chronological order. The first message is always the parent (marked `(parent)` in human output).

For machine-readable output with full metadata:

```bash
slack-cli conversations replies <CHANNEL_ID> <THREAD_TS> --json
```

The JSON output includes `user`, `text`, `ts`, `blocks`, reactions, and attachments for each message.

For long threads, increase the limit:

```bash
slack-cli conversations replies <CHANNEL_ID> <THREAD_TS> --limit 500
```

### Step 3: Resolve User Names (if needed)

Thread messages show user IDs (e.g., `U07MBKFRLAG`), not display names. To resolve:

```bash
slack-cli users info <USER_ID> --json
```

The `real_name` or `display_name` fields give you the human-readable name. Cache these to avoid repeated lookups.

### Step 4: Post a Threaded Reply

```bash
slack-cli chat post <CHANNEL_ID> "Your reply text here" --thread-ts <THREAD_TS>
```

The `--thread-ts` flag is what makes it a thread reply instead of a top-level message. Use the parent message's `ts` value.

### Step 5: Post a Rich Reply with Block Kit

```bash
slack-cli chat post <CHANNEL_ID> "Fallback text" --thread-ts <THREAD_TS> --blocks '[{"type":"section","text":{"type":"mrkdwn","text":"*Summary:* Here is what I found..."}}]'
```

The `text` argument serves as the notification/fallback text. The `--blocks` JSON controls the visual layout.

## Examples

### Read a thread and summarize it

```bash
# Get the thread
slack-cli conversations replies C0AM2BVMHRT 1712345678.123456 --json

# Reply with a summary
slack-cli chat post C0AM2BVMHRT "Here is the summary of this thread..." --thread-ts 1712345678.123456
```

### Find threads in a channel, then read one

```bash
# Pull recent messages, look for threads
slack-cli conversations history C08ACMRDC04 --limit 30 --json

# Read the thread (use the ts of a message that has reply_count > 0)
slack-cli conversations replies C08ACMRDC04 1712000000.000100 --json
```

### Reply to a thread without unfurling links

```bash
slack-cli chat post C0AM2BVMHRT "Check this out: https://example.com" --thread-ts 1712345678.123456 --no-unfurl
```

### Add a reaction to a message in a thread

```bash
slack-cli reactions add C0AM2BVMHRT 1712345678.234567 white_check_mark
```

## Tips

- The `thread_ts` is always the **parent message's** timestamp, not a reply's timestamp. Even when replying to a reply, use the original parent `ts`.
- Slack timestamps look like `1712345678.123456` -- they are unique message identifiers, not just time values.
- Use `--json` when you need to parse thread contents programmatically. The human-readable output truncates long messages to 120 characters.
- To get a permalink to a specific message in a thread: `slack-cli chat permalink <CHANNEL_ID> <MESSAGE_TS>`
- Thread replies do NOT appear in channel history by default. You must use `conversations replies` to see them.
- If a thread has more than 1000 replies (rare), you may need to paginate using the raw API: `slack-cli api conversations.replies --params '{"channel":"C123","ts":"1712345678.123456","cursor":"..."}'`
