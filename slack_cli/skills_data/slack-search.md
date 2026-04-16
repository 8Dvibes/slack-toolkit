---
name: slack-search
description: "Search Slack messages and files by keyword. Supports search operators, sorting, pagination. Requires xoxp- user token. Use when finding past messages, locating files, or querying conversation history."
command_name: slack-cli
tags: [slack, search, messages, files, query]
---
<!-- installed by slack-cli -->

# /slack-search -- Search Slack Messages and Files

Search across the entire Slack workspace for messages and files using Slack's search syntax.

## Prerequisites

Search requires a **user token** (xoxp-). Bot tokens (xoxb-) cannot use the search API. Verify your profile has a user token:

```bash
slack-cli config show
```

If no user token is configured, add one:

```bash
slack-cli config set-profile <name> --bot-token xoxb-... --user-token xoxp-...
```

## Procedure

### Step 1: Search Messages

```bash
slack-cli search messages "your search query"
```

With options:

```bash
# Sort by timestamp (newest first -- the default)
slack-cli search messages "deploy failed" --sort timestamp --sort-dir desc

# Sort by relevance score
slack-cli search messages "deploy failed" --sort score

# Limit results
slack-cli search messages "deploy failed" --count 20

# JSON output for piping
slack-cli search messages "deploy failed" --json
```

### Step 2: Search Files

```bash
slack-cli search files "quarterly report"

# Sort by most recent
slack-cli search files "quarterly report" --sort timestamp --sort-dir desc

# Limit results
slack-cli search files "budget" --count 10 --json
```

### Step 3: Use Search Operators

Slack search supports powerful operators to narrow results:

#### By Person

```
from:@username          Messages from a specific user
from:me                 Messages you sent
to:me                   Direct messages to you
```

#### By Channel

```
in:#channel-name        Messages in a specific channel
in:@username            Messages in a DM with that user
```

#### By Date

```
before:2026-04-01       Messages before a date
after:2026-03-01        Messages after a date
on:2026-04-10           Messages on a specific date
during:march            Messages during a month
during:2026             Messages during a year
```

#### By Content Type

```
has:link                Messages containing a URL
has:reaction            Messages with reactions
has:star                Starred messages
has:pin                 Pinned messages
has::emoji_name:        Messages with a specific reaction
```

#### By File Type

```
type:pdf                PDF files
type:image              Images
type:snippet            Code snippets
type:doc                Documents
```

#### Exact Match

```
"exact phrase"          Match the exact phrase
```

### Step 4: Combine Operators

Operators can be combined for precise searches:

```bash
# Messages from Tyler in #ops channel after March 1
slack-cli search messages "from:@tyler in:#ops after:2026-03-01"

# Links shared in a channel this week
slack-cli search messages "in:#general has:link after:2026-04-07"

# PDF files uploaded by a specific person
slack-cli search files "from:@sara type:pdf"

# Exact phrase in a specific channel before a date
slack-cli search messages '"deploy to production" in:#engineering before:2026-04-01'

# Messages with reactions in a channel
slack-cli search messages "in:#announcements has:reaction"

# Find error discussions from the last month
slack-cli search messages "error OR failure after:2026-03-10 in:#ops"
```

### Step 5: Process Results

For message results, key fields in JSON output:

- `messages.matches[].text` -- the message text
- `messages.matches[].channel.id` -- channel ID
- `messages.matches[].channel.name` -- channel name
- `messages.matches[].user` -- user ID who posted
- `messages.matches[].ts` -- message timestamp (use for threading, reactions, etc.)
- `messages.matches[].permalink` -- direct link to the message

For file results, key fields:

- `files.matches[].name` -- filename
- `files.matches[].filetype` -- file extension
- `files.matches[].user` -- uploader user ID
- `files.matches[].channels[]` -- channels the file was shared in
- `files.matches[].url_private` -- download URL (requires auth)

## Example Workflows

### Find and Reply to a Specific Message

```bash
# Search for the message
slack-cli search messages "quarterly OKR update from:@tyler" --count 1 --json

# Extract channel and ts from results, then reply
slack-cli chat post <channel_id> "Here's the follow-up" --thread-ts <message_ts>
```

### Audit All Links Shared in a Channel

```bash
slack-cli search messages "has:link in:#general after:2026-04-01" --count 100 --json
```

### Find All Files from a User

```bash
slack-cli search files "from:@sara" --sort timestamp --sort-dir desc --count 50 --json
```

## Tips

- **User token required.** If you get `missing_scope` or `not_allowed_token_type`, you need a user token (xoxp-), not a bot token.
- **Search indexes with a slight delay.** Very recently posted messages (within seconds) may not appear in search results immediately.
- **Pagination.** Slack search returns paginated results. Use `--count` to control page size (max 100). For exhaustive searches, you may need to call the raw API with pagination parameters via `slack-cli api search.messages --params '{"query":"...","page":2}'`.
- **Boolean operators.** Use `OR` (must be uppercase) between terms. `AND` is implicit. There is no `NOT` operator; use the minus sign instead: `deploy -staging` finds "deploy" but excludes "staging".
- **Wildcard.** Slack search does not support wildcards (`*`). It does support prefix matching on some terms automatically.
- **Rate limits.** Search API has stricter rate limits than other Slack APIs (Tier 2: ~20 requests per minute). Avoid tight loops.
- **Private channels.** Search results respect the user's access. The user token can only find messages in channels the token owner has access to.
