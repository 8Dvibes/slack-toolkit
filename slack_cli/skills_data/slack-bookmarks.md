---
name: slack-bookmarks
description: "Manage Slack channel bookmarks: add, edit, list, and remove bookmark links pinned to channel headers."
command_name: slack-cli
tags: [slack, bookmarks, links, channels, pinned]
---
<!-- installed by slack-cli -->

# /slack-bookmarks -- Channel Bookmark Management

Add and manage bookmarks that appear in Slack channel headers for quick access to important links.

## Arguments

- `/slack-bookmarks add <channel> <title> <url>` -- Add a bookmark to a channel
- `/slack-bookmarks list <channel>` -- List bookmarks in a channel

## Required Scope

Bot token needs: `bookmarks:write` (add/edit/remove), `bookmarks:read` (list)

## Procedure

### Step 1: List existing bookmarks

```bash
slack-cli bookmarks list C08ACMRDC04

# JSON for scripting
slack-cli bookmarks list C08ACMRDC04 --json
```

### Step 2: Add a bookmark

```bash
# Basic bookmark
slack-cli bookmarks add C08ACMRDC04 "Team Docs" "https://notion.so/your-team-docs"

# With emoji icon
slack-cli bookmarks add C08ACMRDC04 "Sprint Board" "https://linear.app/your-team" --emoji ":chart_with_upwards_trend:"

# Notion page
slack-cli bookmarks add C08ACMRDC04 "Project Notes" "https://notion.so/project-notes" --emoji ":notebook:"
```

### Step 3: Edit an existing bookmark

First get the bookmark ID from the list, then:

```bash
# Update the title and URL
slack-cli bookmarks edit C08ACMRDC04 Bk0XXXXXXXXX --title "Updated Title" --link "https://new-url.com"

# Update just the emoji
slack-cli bookmarks edit C08ACMRDC04 Bk0XXXXXXXXX --emoji ":star:"
```

### Step 4: Remove a bookmark

```bash
slack-cli bookmarks remove C08ACMRDC04 Bk0XXXXXXXXX
```

## Worked Examples

### Set up standard bookmarks for a new project channel

```bash
CHANNEL="C0XXXXXXXXX"

# Project brief
slack-cli bookmarks add "$CHANNEL" "Project Brief" "https://notion.so/brief" --emoji ":memo:"

# Linear board
slack-cli bookmarks add "$CHANNEL" "Sprint Board" "https://linear.app/team/board" --emoji ":dart:"

# GitHub repo
slack-cli bookmarks add "$CHANNEL" "GitHub Repo" "https://github.com/org/repo" --emoji ":octopus:"

# Slack archive / export
slack-cli bookmarks add "$CHANNEL" "Meeting Notes" "https://your-docs-url.com" --emoji ":spiral_note_pad:"

echo "Set up 4 bookmarks for $CHANNEL"
```

### Copy bookmarks from one channel to another

```bash
SOURCE="C0AAAAAAA"
TARGET="C0BBBBBBB"

# Get source bookmarks
BOOKMARKS=$(slack-cli bookmarks list "$SOURCE" --json)

# Add each bookmark to the target
echo "$BOOKMARKS" | python3 -c "
import json, sys, subprocess

bookmarks = json.load(sys.stdin)
for bm in bookmarks:
    cmd = ['slack-cli', 'bookmarks', 'add', '$TARGET',
           bm['title'], bm['link']]
    if bm.get('emoji'):
        cmd += ['--emoji', bm['emoji']]
    subprocess.run(cmd)
    print(f'Added: {bm[\"title\"]}')
"
```

### Audit all bookmarks in a channel

```bash
slack-cli bookmarks list C08ACMRDC04 --json | python3 -c "
import json, sys
bookmarks = json.load(sys.stdin)
for bm in bookmarks:
    print(f\"{bm['id']}: {bm['title']} -> {bm['link']}\")
print(f'Total: {len(bookmarks)} bookmark(s)')
"
```

## Tips

- Bookmark IDs start with `Bk` (e.g. `Bk0XXXXXXXXX`) -- always use `--json` to capture them.
- Each channel can have multiple bookmarks; they appear in order in the channel header.
- Emoji shortcodes work (`:rocket:`, `:memo:`, etc.) -- the Slack app renders them as emoji icons.
- Bookmarks appear to all channel members -- they're not user-specific.
- Use bookmarks to surface important links: Notion docs, Linear boards, GitHub repos, Figma files.
