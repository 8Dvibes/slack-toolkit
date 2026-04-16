# Blueprint: slack-toolkit -- Zero-Dependency Slack CLI for AI Agents

**Status:** Draft (not published)
**Version:** 0.2.2
**Date:** 2026-04-16
**Repo:** github.com/8Dvibes/slack-toolkit

---

## What Was Built

`slack-toolkit` is a zero-dependency Python CLI for the Slack Web API. It ships with a 306-method catalog, 33 Claude Code skills, and a raw API passthrough that lets any AI agent call the full Slack surface without managing OAuth flows, without installing external packages, and without wiring up an MCP server.

Install it once and every agent on every machine can post to Slack, search channels, manage users, create canvases, set reminders, and do anything else the Slack Web API supports -- all from a single scriptable binary.

---

## The Problem It Solves

### AI agents post as the wrong identity

The most common Slack MCP pattern in the community today uses the Claude AI Slack MCP server. It works, but it has a critical limitation: it posts from the claude.ai bot account, not from your own Slack app. Every message shows up as coming from Claude, not from your agent.

If you are building a custom agent -- a morning briefing bot, an ops notifier, a student support system -- you want messages to come from a named bot account that you control. You want your own app name, your own icon, your own OAuth scopes. The MCP server cannot give you that.

`slack-toolkit` authenticates with your own bot token (`xoxb-`). Every message, every reaction, every file upload happens as your app.

### MCP servers are hard to distribute

MCP servers require a running process, a config entry in every client that uses them, and working out OAuth or token injection for each machine. When you onboard a new agent on a new machine, you have to set up the MCP again.

`slack-toolkit` is a CLI binary. `pip install slack-toolkit`, set `SLACK_BOT_TOKEN`, and the agent can post. No config files, no server process, no per-client wiring.

### The API surface is larger than any MCP covers

The Slack Web API has over 300 methods. MCP servers implement a curated subset -- usually 8-12 methods covering the most common operations. That is fine for basic use, but it leaves a lot on the table.

`slack-toolkit` ships the entire method surface in a local catalog. Any method that exists in the Slack API can be called via the raw passthrough. The catalog tells you what parameters it needs, what scopes it requires, and whether to use a bot or user token.

### Scripting is painful without a dedicated tool

Curl-based Slack scripting is verbose and error-prone. You have to remember the endpoint format, handle token headers, parse responses, deal with rate limiting, and manage pagination yourself. For one-off scripts that is tolerable. For an agent that calls Slack 50 times a session, it is not.

`slack-toolkit` handles all of that: rate-limit retry with exponential backoff, cursor-based auto-pagination, token type resolution per method, atomic config writes, structured output with `--json` on every command.

---

## How to Install and Use It

### Install

```bash
uv tool install slack-toolkit
# or
pip install slack-toolkit
```

No external dependencies. Python 3.9+ required.

### Configure

Create a Slack app at [api.slack.com/apps](https://api.slack.com/apps). Add the OAuth scopes your use case needs, install the app to your workspace, and copy the bot token.

```bash
slack-cli config set-profile default \
  --bot-token xoxb-your-token-here \
  --workspace-name "My Workspace"
```

Or for CI/automation, just set the env var:

```bash
export SLACK_BOT_TOKEN=xoxb-your-token-here
```

### First commands

```bash
# Verify the connection
slack-cli api auth.test

# Post a message
slack-cli chat post C0YOURCHANNEL "Hello from slack-toolkit"

# Search channels
slack-cli conversations list

# Look up a user by email
slack-cli users lookup --email jane@example.com
```

### Multiple workspaces

```bash
slack-cli config set-profile prod --bot-token xoxb-prod-...
slack-cli config set-profile staging --bot-token xoxb-staging-...
slack-cli config set-default prod

# Switch with --profile or SLACK_PROFILE env var
slack-cli --profile staging chat post C0CHANNEL "staging test"
```

---

## The Skill System

The 33 bundled Claude Code skills are the fastest way to put slack-toolkit to work with AI agents.

### Install the skills

```bash
slack-cli skills install
```

This copies 33 SKILL.md files to `~/.claude/skills/`. Each skill teaches Claude Code how to handle a specific category of Slack task.

### Invoke from Claude Code

```
/slack-post C0CHANNEL "Deploy complete"
/slack-search "error in staging last 24 hours"
/slack-channel-create ops-team-north
/slack-user-lookup jane@example.com
```

### The 33 skills at a glance

Skills are organized into two layers: **Layer 1** (operational skills -- what to do) and **Layer 2** (expert skills -- how to do it right).

#### Layer 1: Operational Skills (28)

| Skill | What it handles |
|-------|----------------|
| `/slack-post` | Posting messages with Block Kit, threads, scheduling |
| `/slack-thread` | Reading and replying to threads |
| `/slack-schedule` | Scheduled message delivery |
| `/slack-search` | Full-text message and file search |
| `/slack-file-upload` | File upload via the V2 two-step flow |
| `/slack-reactions` | Emoji reactions, emoji polls |
| `/slack-channel-create` | End-to-end channel provisioning |
| `/slack-channel-info` | Deep channel inspection |
| `/slack-user-lookup` | User lookup by email, ID, name |
| `/slack-status` | Workspace health check |
| `/slack-bulk-ops` | Bulk operations with dry-run |
| `/slack-archive-export` | Export history to Markdown |
| `/slack-audit` | Read-only workspace audit |
| `/slack-emoji` | Custom emoji listing |
| `/slack-dynamic` | **Meta-skill**: call any of 306 API methods dynamically |
| `/slack-dm` | DM and group DM creation |
| `/slack-identity` | Token verification and scope audit |
| `/slack-canvas` | Canvas CRUD and access control |
| `/slack-usergroup` | User group management |
| `/slack-reminders` | Reminder CRUD |
| `/slack-streaming` | AI response streaming into Slack |
| `/slack-assistant` | Slack AI assistant thread management |
| `/slack-docs` | Live API doc lookup from docs.slack.dev |
| `/slack-lists` | Slack Lists CRUD |
| `/slack-dnd` | Do Not Disturb management |
| `/slack-admin` | Admin operations via passthrough |
| `/slack-calls` | Voice/video call registration |
| `/slack-bookmarks` | Channel bookmark management |

#### Layer 2: Expert Skills (5)

These skills teach agents the underlying mechanics of the Slack API -- not just what commands to run, but how to debug failures, choose the right token type, build rich messages correctly, and resolve problems without human escalation.

| Skill | What it handles |
|-------|----------------|
| `/slack-api-expert` | Master guide: token types, pagination, rate limits, self-service resolution chain, source reading |
| `/slack-block-kit` | Build rich messages with Block Kit: all block types, 5 ready-to-use templates, shell quoting patterns |
| `/slack-integration-patterns` | 6 architectural patterns: notification pipeline, approval flow, report posting, channel provisioning |
| `/slack-mrkdwn` | Complete Slack markup syntax reference with markdown comparison, mentions, date formatting, escaping |
| `/slack-troubleshooting` | Self-diagnosis guide for 15 common API errors: scope issues, token debugging, escalation chain |

### Building your own skills

Skills are Markdown files. Drop a `.md` file in `~/.claude/skills/` and it is immediately available as a slash command in Claude Code. The format is:

```markdown
---
name: my-skill-name
description: "One-line description for Claude's skill picker"
command_name: slack-cli
tags: [slack, custom, whatever]
---

# /my-skill-name -- What It Does

## Procedure

### Step 1

```bash
slack-cli conversations list --json
```

## Tips

- Gotcha or non-obvious behavior here.
```

The frontmatter `description` is what Claude reads when matching a user request to available skills. Make it specific about when to use the skill.

---

## The Dynamic Pattern

`/slack-dynamic` is the most important skill in the kit. It unlocks the full Slack API surface for any AI agent using a consistent three-step loop.

The insight is that the catalog already knows everything about every method. Instead of implementing 306 CLI commands, you give the agent a search interface and a raw passthrough, and let it compose them on the fly.

**Step 1: Search**

```bash
slack-cli methods search <keyword>
```

Searches method names, namespaces, descriptions, and parameter names. Returns ranked results from the 306-method catalog. Instant, offline.

**Step 2: Read the spec**

```bash
slack-cli methods get <method.name>
```

Returns: description, required params with descriptions, optional params, token types (bot vs user), required OAuth scopes, rate tier, pagination details, and deprecation status. Everything the agent needs to call the method correctly.

**Step 3: Call it**

```bash
slack-cli api <method.name> --params '{"key": "value"}' [--token-type bot|user]
```

The raw passthrough returns the full Slack API response as JSON.

This pattern means the agent never hits a capability wall. If the Slack API supports it and the app has the right scopes, the agent can do it.

---

## Architecture Decisions

### Zero dependencies

No external packages. The entire CLI runs on Python stdlib: `urllib` for HTTP, `json` for serialization, `ssl` for TLS, `argparse` for the command surface. This was a deliberate constraint, not an accident.

Zero dependencies means no supply chain risk, no version conflicts, no "this requires numpy 1.x but you have numpy 2.x" problems on any machine in the fleet. The binary installs clean and stays clean.

It also means the tool is easy to audit. If you need to verify it does what it says, you are reading straightforward Python with no abstraction layers underneath.

### The catalog pattern

The method catalog decouples capability discovery from CLI release cadence. When Slack adds a new method, you do not need a new version of slack-toolkit to call it -- you can call it immediately via the raw passthrough. The catalog updates with `methods update --live` to pull the new method name and params.

This is the same pattern that makes n8n-cli useful: a structured, locally-queryable index of the full API surface, bundled with the tool, independently updatable.

### Skill bundling inside the wheel

Skills ship as `package-data` inside the Python wheel. When you `pip install slack-toolkit`, the 33 SKILL.md files come along. `slack-cli skills install` copies them to `~/.claude/skills/`. One install, one skills-install, you are done.

The alternative -- hosting skills separately or requiring a manual download -- adds friction that kills adoption. Community members should be able to go from zero to working skills in two commands.

### Profile isolation

Each Slack workspace is a named profile in `~/.slack-cli.json` (mode 600). The active profile is resolved via: explicit `--profile` flag, then `SLACK_PROFILE` env var, then the `default_profile` field in config. Env vars (`SLACK_BOT_TOKEN`, `SLACK_USER_TOKEN`) override config entirely.

This makes it straightforward to manage multiple workspaces (production, staging, client workspaces) and to use the tool in CI without touching the config file.

### Rate-limit handling built in

The HTTP client retries up to 5 times on 429 responses. It reads the `Retry-After` header and adds exponential backoff with jitter. This is invisible to the caller -- commands just run, and if Slack is temporarily overloaded, they wait and retry automatically.

---

## Scope vs n8n-cli

`slack-toolkit` is a companion tool to n8n-cli, not a replacement. The two tools solve adjacent problems:

- `n8n-cli` is for managing and building n8n workflow automations. It is about the orchestration layer.
- `slack-toolkit` is for calling the Slack API directly. It is about the communication layer.

In practice they compose well: n8n handles your workflow logic, and when that workflow needs to post to Slack with a specific bot identity or manage channel membership, slack-toolkit is the right tool for the CLI-layer calls.

---

## What Comes Next

Ideas for future versions -- none of these are committed yet:

- `slack-cli skills doctor` -- validate that every command referenced in every installed skill actually exists in the current CLI surface (same pattern as n8n-cli)
- Webhook support -- inbound webhook receiver for quick testing
- Expanded admin coverage -- more admin.* namespace commands with dedicated commands (not just passthrough)
- Export formats -- CSV and JSON export flags on more list commands

**Done in v0.2.2:** Block Kit builder coverage is now handled by the `/slack-block-kit` expert skill, which ships 5 ready-to-use templates and covers all block types. No CLI command needed -- the skill gives agents everything required to compose Block Kit JSON correctly.

---

## Community Use Cases

This tool is designed for the AI Build Lab community's specific workflows, but the patterns are general:

- **Morning briefing agents** that post formatted summaries to Slack on a schedule, from a named bot account
- **Student/customer notification pipelines** that need to post to specific channels without touching MCP config
- **Workspace auditing** to find stale channels, missing topics, or permission gaps across large workspaces
- **Onboarding automation** that provisions channels, invites members, and adds bookmarks as part of a larger flow
- **Multi-workspace management** for agencies or teams with separate client workspaces
- **Claude Code skill chains** where one skill posts an intermediate result to Slack while the agent continues working

---

*Draft prepared for Tyler's review. Do not publish.*
