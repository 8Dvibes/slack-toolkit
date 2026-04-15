---
name: slack-docs
description: "Real-time Slack API doc lookup and catalog refresh. Fetch method docs, check staleness, and update the local catalog from docs.slack.dev."
command_name: slack-cli
tags: [slack, docs, catalog, reference, api, methods]
---
<!-- installed by slack-cli -->

# /slack-docs -- API Documentation Lookup

Look up Slack API method documentation, check catalog staleness, and refresh from docs.slack.dev.

## Arguments

- `/slack-docs <method>` -- Fetch docs for a specific method
- `/slack-docs` -- Interactive: ask what method to look up

## When to Use This Skill

- You need parameter details for a Slack API method
- You get an error about a method not existing or a parameter being wrong
- The catalog feels stale (methods missing that you know exist)
- You want to verify required scopes before calling a method

## Procedure

### Step 1: Look up a method

```bash
# Fetch docs for a specific method (cached for 30 days)
slack-cli docs conversations.open

# Force-refresh from docs.slack.dev (bypass cache)
slack-cli docs conversations.open --fresh

# JSON output
slack-cli docs conversations.open --json
```

Docs are cached at `~/.slack-cli/docs/<method>.md`.

### Step 2: Search the local catalog first (faster)

```bash
# Search by keyword
slack-cli methods search conversations

# Get structured details for a method
slack-cli methods get conversations.open

# List all methods in a namespace
slack-cli methods list --namespace conversations
```

### Step 3: Check catalog staleness

```bash
slack-cli methods info
```

If the catalog is >30 days old, you'll see a warning. Update it:

```bash
# Reset to bundled catalog (always works, offline)
slack-cli methods update

# Fetch live updates from docs.slack.dev (requires internet)
slack-cli methods update --live
```

### Step 4: Verify a method exists

```bash
slack-cli methods get admin.conversations.bulkArchive --json
# Returns null if not found
```

If a method is missing from the catalog but you know it exists, run:
```bash
slack-cli methods update --live
```

## Decision Tree

When you need info about a Slack method:

1. **Try `slack-cli methods get <method>`** -- fast, offline, structured
2. **If not found**: run `slack-cli methods update --live`, then retry
3. **Need full parameter details**: run `slack-cli docs <method>` to fetch the live page
4. **If docs fetch fails**: use `slack-cli api <method> --params '{}'` and read the error response

## Tips

- The catalog has 306 methods covering the full Slack API surface.
- Docs cache lives at `~/.slack-cli/docs/` -- delete any file to force a refresh.
- The `methods search` command accepts partial names: `slack-cli methods search bulk` finds all bulk methods.
- For admin methods that require special setup, always check the docs -- required params are often undocumented in the catalog.
- Use `slack-cli methods namespaces` to see the full list of API namespaces (admin, apps, canvas, etc.).
