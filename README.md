# slack-toolkit

Zero-dependency CLI for the Slack Web API. 306 API methods in the catalog, 28 Claude Code skills bundled, no external packages required.

Built for AI agents, automation scripts, and developers who need a scriptable Slack client without managing OAuth flows in a browser or wiring up MCP servers.

---

## Quick Start

**1. Install**

```bash
pip install slack-toolkit
# or with uv (recommended for isolated install)
uv tool install slack-toolkit
```

**2. Create a Slack app and generate tokens**

Go to [api.slack.com/apps](https://api.slack.com/apps), create an app, add OAuth scopes, and install it to your workspace. You need at minimum `chat:write` for the bot token.

**3. Configure your profile**

```bash
slack-cli config set-profile default \
  --bot-token xoxb-your-bot-token \
  --workspace-name "My Workspace"
```

Or set an environment variable for quick use:

```bash
export SLACK_BOT_TOKEN=xoxb-your-bot-token
```

**4. Verify the connection**

```bash
slack-cli api auth.test
```

**5. Post your first message**

```bash
slack-cli chat post C0YOURCHANNEL "Hello from slack-cli"
```

---

## Why Not Just Use the Slack MCP?

The `@modelcontextprotocol/server-slack` MCP works for basic operations. But it has three limitations:

1. **Identity.** The MCP server posts as whatever OAuth identity it's configured with. If your Claude session has a remote Slack MCP connection, messages go out as your personal account, not as a named bot. `slack-cli` always uses your bot token, so every message is from your app.

2. **Coverage.** The Slack MCP exposes ~15 tools. The Slack API has 306 methods. `slack-cli` ships the full catalog and a raw passthrough, so nothing is out of reach.

3. **Distribution.** MCP servers require a running process and per-client config on every machine. `slack-cli` is a single binary. Install once, set a token, done.

If the MCP covers your needs and identity doesn't matter, keep using it. If you need a specific bot identity, full API access, or fleet-wide deployment, `slack-cli` is the tool.

---

## Features

### 306-Method Catalog

The full Slack Web API surface is bundled as a local JSON catalog. Search it instantly, get parameter details, required scopes, rate tier, and token type for any method -- all offline.

```bash
slack-cli methods search usergroups
slack-cli methods get conversations.open
slack-cli methods list --namespace admin.conversations
```

The catalog auto-warns when it's more than 30 days old. Update with `slack-cli methods update` (reset to bundled) or `slack-cli methods update --live` (fetch from docs.slack.dev).

### Per-Method Documentation

Fetch and cache full method documentation straight from docs.slack.dev:

```bash
slack-cli docs conversations.open
slack-cli docs chat.postMessage --fresh  # bypass cache
```

Docs are cached in `~/.slack-cli/docs/` with a 30-day TTL.

### 28 Claude Code Skills

Skills are structured prompt files that teach Claude Code how to use slack-cli for common tasks. Install them all in one command:

```bash
slack-cli skills install
```

Then invoke any skill from Claude Code: `/slack-post`, `/slack-dynamic`, `/slack-channel-create`, etc.

### Zero Dependencies

The entire tool runs on Python stdlib. No `requests`, no `slack_sdk`, no transitive dependency surface to audit. Install it once, run it anywhere Python 3.9+ exists.

### Raw API Passthrough

Call any Slack API method directly without waiting for a dedicated command to exist:

```bash
slack-cli api admin.conversations.bulkArchive \
  --params '{"channel_ids": ["C123", "C456"]}' \
  --token-type user
```

### Profile-Based Configuration

Manage multiple workspaces with named profiles:

```bash
slack-cli config set-profile prod --bot-token xoxb-prod-...
slack-cli config set-profile staging --bot-token xoxb-staging-...
slack-cli config set-default prod

# Switch profiles per command
slack-cli --profile staging chat post C0CHANNEL "test message"

# Or via env var
SLACK_PROFILE=staging slack-cli conversations list
```

Config lives at `~/.slack-cli.json` (mode 600).

---

## Command Reference

### Global Flags

```
--profile PROFILE   Use a named config profile
--json              Output raw JSON (works on most commands)
--help              Show help for any command or subcommand
```

---

### `config`

Manage profiles and workspace credentials.

```bash
# Show current config
slack-cli config show

# Create or update a profile
slack-cli config set-profile myworkspace \
  --bot-token xoxb-... \
  --user-token xoxp-... \
  --workspace-name "My Workspace" \
  --default-channel C0GENERAL

# Set which profile is used by default
slack-cli config set-default myworkspace

# Remove a profile
slack-cli config remove-profile myworkspace
```

---

### `chat`

Post, update, delete, and schedule messages.

```bash
# Post a message
slack-cli chat post C0CHANNEL "Hello world"
slack-cli chat post C0CHANNEL "No link previews" --no-unfurl

# Post with Block Kit
slack-cli chat post C0CHANNEL "Fallback text" --blocks '[
  {"type": "header", "text": {"type": "plain_text", "text": "Alert"}},
  {"type": "section", "text": {"type": "mrkdwn", "text": "*Status:* All good"}}
]'

# Reply in a thread
slack-cli chat post C0CHANNEL "Thread reply" --thread-ts 1712345678.000100

# Update a message
slack-cli chat update C0CHANNEL 1712345678.000100 --text "Updated text"

# Delete a message
slack-cli chat delete C0CHANNEL 1712345678.000100

# Schedule a message (Unix timestamp)
slack-cli chat schedule C0CHANNEL "Good morning" 1712400000

# List scheduled messages
slack-cli chat schedule-list
slack-cli chat schedule-list --channel C0CHANNEL

# Cancel a scheduled message
slack-cli chat schedule-delete C0CHANNEL Sm1234567890abcdef

# Get permalink to a message
slack-cli chat permalink C0CHANNEL 1712345678.000100
```

---

### `conversations`

List, inspect, create, and manage channels and DMs.

```bash
# List channels the bot is in
slack-cli conversations list
slack-cli conversations list --types public_channel,private_channel --limit 50

# Get channel info
slack-cli conversations info C0CHANNEL

# Get message history
slack-cli conversations history C0CHANNEL --limit 20
slack-cli conversations history C0CHANNEL --oldest 1712000000 --latest 1712400000

# Get thread replies
slack-cli conversations replies C0CHANNEL --ts 1712345678.000100

# Get members
slack-cli conversations members C0CHANNEL

# Create a channel
slack-cli conversations create my-new-channel
slack-cli conversations create my-private-channel --private

# Archive / unarchive
slack-cli conversations archive C0CHANNEL
slack-cli conversations unarchive C0CHANNEL

# Join / leave
slack-cli conversations join C0CHANNEL
slack-cli conversations leave C0CHANNEL

# Invite users
slack-cli conversations invite C0CHANNEL --users U0USER1 U0USER2

# Kick a user
slack-cli conversations kick C0CHANNEL --user U0USER1

# Open a DM or group DM
slack-cli conversations open --users U0USER1 U0USER2

# Invite all workspace members (supports --dry-run)
slack-cli conversations invite-all C0CHANNEL --dry-run
slack-cli conversations invite-all C0CHANNEL

# Clone members from one channel to another
slack-cli conversations clone-members --from-channel C0SOURCE --to-channel C0DEST --dry-run
slack-cli conversations clone-members --from-channel C0SOURCE --to-channel C0DEST

# Export member list
slack-cli conversations export-members C0CHANNEL
slack-cli conversations export-members C0CHANNEL --format csv
slack-cli conversations export-members C0CHANNEL --format json

# Compare two channel membership lists
slack-cli conversations diff C0CHANNEL_A C0CHANNEL_B

# Pick a random member
slack-cli conversations random C0CHANNEL

# Find inactive members (no posts in N days)
slack-cli conversations inactive C0CHANNEL --days 30
slack-cli conversations inactive C0CHANNEL --days 14 --dry-run

# Set topic / purpose
slack-cli conversations topic C0CHANNEL "New topic text"
slack-cli conversations purpose C0CHANNEL "New purpose text"
```

---

### `users`

Look up users by email, ID, or browse the workspace.

```bash
# Search users by name
slack-cli users search "Jane"

# Get user info by ID
slack-cli users info U0USERID

# Lookup by email
slack-cli users lookup --email jane@example.com

# Get full profile
slack-cli users profile U0USERID

# List all users
slack-cli users list
slack-cli users list --limit 200

# Check presence
slack-cli users presence U0USERID

# Set your own presence
slack-cli users set-presence away
slack-cli users set-presence auto
```

---

### `search`

Full-text search across messages and files. Requires a user token (`xoxp-`).

```bash
# Search messages
slack-cli search messages "deployment failed"
slack-cli search messages "from:@jane in:#ops" --sort timestamp --sort-dir desc

# Search files
slack-cli search files "Q4 report"

# Search everything
slack-cli search all "kubernetes"
```

---

### `files`

Upload, list, and manage files.

```bash
# Upload a file
slack-cli files upload /path/to/report.pdf --channels C0CHANNEL1 C0CHANNEL2
slack-cli files upload /path/to/image.png --channels C0CHANNEL --title "Screenshot" --comment "See attachment"
slack-cli files upload /path/to/log.txt --channels C0CHANNEL --thread-ts 1712345678.000100

# List files
slack-cli files list
slack-cli files list --channel C0CHANNEL
slack-cli files list --user U0USERID
slack-cli files list --types images

# Get file info
slack-cli files info F0FILEID

# Delete a file
slack-cli files delete F0FILEID
```

---

### `reactions`

Add, remove, and inspect emoji reactions.

```bash
# Add a reaction
slack-cli reactions add C0CHANNEL 1712345678.000100 white_check_mark

# Remove a reaction
slack-cli reactions remove C0CHANNEL 1712345678.000100 white_check_mark

# Get reactions on a message
slack-cli reactions get C0CHANNEL 1712345678.000100

# List all reactions by the authed user
slack-cli reactions list
slack-cli reactions list --user U0USERID
```

---

### `pins`

Pin and unpin messages in channels.

```bash
# Pin a message
slack-cli pins add C0CHANNEL 1712345678.000100

# Unpin a message
slack-cli pins remove C0CHANNEL 1712345678.000100

# List pinned items
slack-cli pins list C0CHANNEL
```

---

### `bookmarks`

Manage bookmarks pinned to channel headers.

```bash
# Add a bookmark
slack-cli bookmarks add C0CHANNEL "AI Build Lab" https://aibuildlab.com
slack-cli bookmarks add C0CHANNEL "Runbook" https://docs.example.com --emoji books

# Edit a bookmark
slack-cli bookmarks edit C0CHANNEL Bm0BOOKMARKID --title "New Title" --link https://newurl.com

# List bookmarks
slack-cli bookmarks list C0CHANNEL

# Remove a bookmark
slack-cli bookmarks remove C0CHANNEL Bm0BOOKMARKID
```

---

### `usergroups`

Create and manage @-mention user groups.

```bash
# Create a user group
slack-cli usergroups create "On-Call Team" --handle on-call
slack-cli usergroups create "Leads" --handle leads --description "Team leads" --channels C0CHANNEL1

# List user groups
slack-cli usergroups list
slack-cli usergroups list --include-disabled

# Update a user group
slack-cli usergroups update S0GROUPID --name "New Name" --handle new-handle

# Disable / enable
slack-cli usergroups disable S0GROUPID
slack-cli usergroups enable S0GROUPID

# List members
slack-cli usergroups members list S0GROUPID

# Update members
slack-cli usergroups members update S0GROUPID --users U0USER1 U0USER2 U0USER3
```

---

### `canvas`

Create and manage Slack Canvases.

```bash
# Create a canvas
slack-cli canvas create --title "Project Brief"
slack-cli canvas create --title "Channel Doc" --channel C0CHANNEL
slack-cli canvas create --title "Runbook" --content "# Overview\n\nContent here."

# Edit a canvas
slack-cli canvas edit F0CANVASID --changes '[{"operation": "insert_at_end", "document_content": {"type": "md", "markdown": "## New Section"}}]'

# Delete a canvas
slack-cli canvas delete F0CANVASID

# Set access level
slack-cli canvas access set F0CANVASID --access-level write --users U0USER1 U0USER2
slack-cli canvas access set F0CANVASID --access-level read --channels C0CHANNEL

# Remove access
slack-cli canvas access delete F0CANVASID --users U0USER1

# List sections
slack-cli canvas sections F0CANVASID
slack-cli canvas sections F0CANVASID --contains-text "overview"
```

---

### `reminders`

Set and manage reminders.

```bash
# Add a reminder (requires user token)
slack-cli reminders add "Review the PR" "in 2 hours"
slack-cli reminders add "Weekly sync prep" "tomorrow at 9am"
slack-cli reminders add "Check deploy" 1712400000  # Unix timestamp

# List reminders
slack-cli reminders list

# Get reminder details
slack-cli reminders info Rm0REMINDERID

# Mark complete
slack-cli reminders complete Rm0REMINDERID

# Delete a reminder
slack-cli reminders delete Rm0REMINDERID
```

---

### `dnd`

Manage Do Not Disturb settings.

```bash
# Check DND status for yourself or a user
slack-cli dnd info
slack-cli dnd info --user U0USERID

# Enable snooze (requires user token)
slack-cli dnd set-snooze --minutes 60

# End snooze
slack-cli dnd end-snooze

# Check team DND status
slack-cli dnd team-info --users U0USER1 U0USER2
```

---

### `methods`

Browse and search the 306-method API catalog.

```bash
# Search by keyword
slack-cli methods search conversations
slack-cli methods search "bulk archive"

# Get full details for a method
slack-cli methods get conversations.open
slack-cli methods get admin.conversations.bulkArchive --json

# List all methods in a namespace
slack-cli methods list --namespace usergroups
slack-cli methods list --namespace admin.conversations

# Show all namespaces
slack-cli methods namespaces

# Catalog stats
slack-cli methods info

# Update catalog (offline reset to bundled)
slack-cli methods update

# Update catalog (live fetch from docs.slack.dev)
slack-cli methods update --live
```

---

### `docs`

Fetch and cache per-method documentation from docs.slack.dev.

```bash
# Fetch docs (cached for 30 days)
slack-cli docs conversations.open
slack-cli docs chat.postMessage

# Force-refresh from docs.slack.dev
slack-cli docs admin.conversations.bulkArchive --fresh

# JSON output with cache metadata
slack-cli docs usergroups.list --json
```

---

### `api`

Raw passthrough to any Slack API method. The escape hatch for anything not covered by a dedicated command.

```bash
# Call any method with JSON params
slack-cli api auth.test
slack-cli api conversations.list --params '{"types": "public_channel", "limit": 10}'

# Methods that need a user token
slack-cli api search.messages --params '{"query": "incident", "count": 20}' --token-type user

# Always returns full JSON response
slack-cli api emoji.list --json
```

---

### `skills`

Manage the bundled Claude Code skills.

```bash
# Install all 28 skills to ~/.claude/skills/
slack-cli skills install

# Force-overwrite even non-slack-cli skills
slack-cli skills install --force

# List bundled skills
slack-cli skills list
slack-cli skills list --json

# Validate skills reference valid CLI commands
slack-cli skills doctor
```

---

## Skills Catalog

28 Claude Code skills ship with slack-toolkit. Install them with `slack-cli skills install` and invoke from any Claude Code session.

| Skill | Command | Description |
|-------|---------|-------------|
| `slack-post` | `/slack-post` | Post messages with Block Kit support, threaded replies, and scheduled delivery |
| `slack-thread` | `/slack-thread` | Read and reply to Slack threads with full conversation context |
| `slack-schedule` | `/slack-schedule` | Schedule messages for future delivery with human-readable time conversion |
| `slack-search` | `/slack-search` | Full-text message and file search using Slack search operators |
| `slack-file-upload` | `/slack-file-upload` | Upload files using the V2 two-step flow with channel sharing |
| `slack-reactions` | `/slack-reactions` | Add/remove reactions, run emoji polls, audit reaction patterns |
| `slack-channel-create` | `/slack-channel-create` | Provision a channel end-to-end: name, topic, members, bookmarks |
| `slack-channel-info` | `/slack-channel-info` | Deep dive on a channel: members, history, pins, bookmarks, purpose |
| `slack-user-lookup` | `/slack-user-lookup` | Look up users by email, ID, or name; check presence and profile |
| `slack-status` | `/slack-status` | Workspace health check: connection, bot info, token scopes |
| `slack-bulk-ops` | `/slack-bulk-ops` | Bulk operations with dry-run: invite users, archive channels, set topics |
| `slack-archive-export` | `/slack-archive-export` | Export channel history to Markdown with username resolution |
| `slack-audit` | `/slack-audit` | Read-only workspace audit: stale channels, missing topics, membership gaps |
| `slack-emoji` | `/slack-emoji` | List and search custom workspace emoji via API passthrough |
| `slack-dynamic` | `/slack-dynamic` | **The meta-skill**: dynamically discover and call any of 306 API methods |
| `slack-dm` | `/slack-dm` | Create DMs and group DMs, resolving emails to user IDs automatically |
| `slack-identity` | `/slack-identity` | Verify posting identity, audit token scopes, confirm bot vs user context |
| `slack-canvas` | `/slack-canvas` | Create, edit, and manage Slack Canvases with access control |
| `slack-usergroup` | `/slack-usergroup` | Manage user groups: create, update, enable/disable, manage members |
| `slack-reminders` | `/slack-reminders` | Create, list, complete, and delete reminders with natural language times |
| `slack-streaming` | `/slack-streaming` | Stream AI responses into Slack via `chat.startStream`/`appendStream`/`stopStream` |
| `slack-assistant` | `/slack-assistant` | Manage Slack AI assistant threads: status, suggested prompts, titles |
| `slack-docs` | `/slack-docs` | Real-time API doc lookup, catalog refresh from docs.slack.dev |
| `slack-lists` | `/slack-lists` | Slack Lists CRUD via API passthrough |
| `slack-dnd` | `/slack-dnd` | Check and set Do Not Disturb: snooze, end snooze, team DND status |
| `slack-admin` | `/slack-admin` | Admin operations via API passthrough: users, channels, apps, workspace settings |
| `slack-calls` | `/slack-calls` | Register and manage voice/video calls in Slack's call UI |
| `slack-bookmarks` | `/slack-bookmarks` | Add, edit, list, and remove channel bookmarks |

---

## The Dynamic Pattern

`/slack-dynamic` is the most important skill in the kit. It teaches Claude Code a three-step pattern for handling any Slack API request, including methods with no dedicated command.

**Step 1: Search the catalog**

```bash
slack-cli methods search <keyword>
```

**Step 2: Read the method spec**

```bash
slack-cli methods get <method.name>
```

This returns: description, required params, optional params, token types, required OAuth scopes, rate tier, pagination details, and deprecation status.

**Step 3: Call via passthrough**

```bash
slack-cli api <method.name> --params '{"key": "value"}' [--token-type bot|user]
```

Example: setting a channel's purpose

```bash
# Find the method
slack-cli methods search purpose

# Read the spec
slack-cli methods get conversations.setPurpose

# Call it
slack-cli api conversations.setPurpose \
  --params '{"channel": "C0CHANNEL", "purpose": "Team ops and coordination"}'
```

Because the catalog covers all 306 Slack Web API methods, this pattern works for everything -- including admin APIs, canvas operations, streaming, and workspace management -- without waiting for a new CLI release.

---

## Keeping Docs Fresh

The method catalog ships with the package and is copied to `~/.slack-cli/methods/catalog.json` on first use.

```bash
# Check catalog age and stats
slack-cli methods info

# Reset to bundled catalog (offline, always works)
slack-cli methods update

# Pull live updates from docs.slack.dev
slack-cli methods update --live
```

Per-method documentation (fetched on demand) caches at `~/.slack-cli/docs/`. Cache files are valid for 30 days. Force a refresh with `--fresh`:

```bash
slack-cli docs conversations.open --fresh
```

---

## Building Your Own Skills

Skills are Markdown files with YAML frontmatter. Create `~/.claude/skills/my-slack-skill.md`:

```markdown
---
name: my-slack-skill
description: "What this skill does"
command_name: slack-cli
tags: [slack, custom]
---

# /my-slack-skill -- What It Does

Brief description.

## Procedure

### Step 1: Do the thing

```bash
slack-cli conversations list --json
```

## Tips

- One tip here.
```

Keep skills focused on a single task area. The best skills follow the same pattern as the bundled ones: a clear procedure section with real command examples, a tips section with gotchas, and frontmatter tags that help Claude match the skill to user intent.

---

## Architecture

```
slack_cli/
  cli.py           -- argparse command tree, entry point
  client.py        -- HTTP client (urllib only), rate-limit retry, pagination
  config.py        -- Profile management, ~/.slack-cli.json
  methods.py       -- Catalog system: search, get, update, staleness check
  docs.py          -- Per-method doc fetcher, HTML parser, 30-day cache
  skills.py        -- Skill installer: copy .md files to ~/.claude/skills/
  api.py           -- Raw API passthrough command
  chat.py          -- Message posting, updates, scheduling
  conversations.py -- Channel/DM management
  users.py         -- User lookup, profile, presence
  search.py        -- Full-text search (requires user token)
  files.py         -- File upload (V2 flow), list, delete
  reactions.py     -- Emoji reactions
  pins.py          -- Pinned messages
  bookmarks.py     -- Channel bookmarks
  usergroups.py    -- User group management
  canvas.py        -- Slack Canvas CRUD
  reminders.py     -- Reminder management
  dnd.py           -- Do Not Disturb
  catalog_data/    -- Bundled methods.json (306 methods)
  skills_data/     -- 28 bundled SKILL.md files
```

**Key design decisions:**

- **Zero dependencies.** The entire tool uses Python stdlib: `urllib` for HTTP, `json` for serialization, `ssl` for TLS, `argparse` for the CLI. No package conflicts, no supply chain risk.
- **Catalog pattern.** The method catalog decouples "what methods exist" from the CLI release cycle. You can update the catalog without upgrading the package.
- **Skill bundling.** Skills ship inside the Python wheel as `package-data`. One install command, one skills-install command -- nothing to manually copy.
- **Profile isolation.** Each workspace is a named profile. Credentials are stored at `~/.slack-cli.json` (mode 600). Env vars override config for CI.
- **Auto-pagination.** The `client.paginate()` method handles cursor-based pagination automatically. The raw `api` passthrough does not paginate -- useful when you need explicit control.
- **Rate-limit handling.** The HTTP client retries up to 5 times on 429 responses, respecting the `Retry-After` header with exponential backoff and jitter.

---

## Contributing

Pull requests are welcome. Please:

1. Keep zero-dependency constraint (Python stdlib only)
2. Add tests for new commands in `tests/test_basic.py`
3. Update the skills catalog if adding new functionality worth teaching Claude

---

## License

MIT. See [LICENSE](LICENSE).
