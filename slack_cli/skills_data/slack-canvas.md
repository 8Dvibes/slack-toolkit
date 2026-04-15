---
name: slack-canvas
description: "Create, edit, and manage Slack canvases. Covers creating standalone canvases, channel canvases, editing sections, and access control."
command_name: slack-cli
tags: [slack, canvas, docs, collaboration, canvases]
---
<!-- installed by slack-cli -->

# /slack-canvas -- Canvas Management

Create and manage Slack canvases for collaborative documentation.

## Arguments

- `/slack-canvas create <title>` -- Create a new canvas with a title
- `/slack-canvas` -- Interactive canvas operations

## Required Scope

Bot token needs: `canvases:write` (create/edit/delete), `canvases:read` (sections lookup)

## Procedure

### Step 1: Create a standalone canvas

```bash
# Simple canvas with just a title
slack-cli canvas create --title "Meeting Notes 2026-04-13"

# Canvas with markdown content
slack-cli canvas create --title "Team Handbook" --content "# Welcome\n\nThis is our team handbook."

# Canvas attached to a channel
slack-cli canvas create --title "Project Alpha Notes" --channel C08ACMRDC04
```

### Step 2: Edit a canvas

Edit operations use a JSON array of change operations:

```bash
# Insert content at the end
slack-cli canvas edit CANVAS_ID --changes '[
  {
    "operation": "insert_at_end",
    "document_content": {
      "type": "markdown",
      "markdown": "## New Section\n\nAdded by automation."
    }
  }
]'
```

Available operations: `insert_at_end`, `insert_before`, `insert_after`, `replace`, `delete`

### Step 3: Manage access

```bash
# Grant read access to specific users
slack-cli canvas access-set CANVAS_ID read --users U07MBKFRLAG,U07M6QW8DML

# Grant write access to a channel
slack-cli canvas access-set CANVAS_ID write --channels C08ACMRDC04

# Revoke access
slack-cli canvas access-delete CANVAS_ID --users U07MBKFRLAG
```

### Step 4: Look up sections

```bash
# List all sections
slack-cli canvas sections CANVAS_ID

# Find sections containing specific text
slack-cli canvas sections CANVAS_ID --contains-text "action items"
```

Section IDs are needed for targeted edits using `insert_before` or `insert_after` operations.

### Step 5: Delete a canvas

```bash
slack-cli canvas delete CANVAS_ID
```

## Worked Examples

### Create a meeting notes canvas and share with team

```bash
# Create
slack-cli canvas create --title "Founders Sync 2026-04-13" --content "## Agenda\n\n1. Status\n2. Blockers\n3. Next steps" --json

# Get canvas ID from response, then grant write access to Tyler and Sara
slack-cli canvas access-set CANVAS_ID write --users U07MBKFRLAG,U07M6QW8DML
```

### Append action items to an existing canvas

```bash
slack-cli canvas edit CANVAS_ID --changes '[
  {
    "operation": "insert_at_end",
    "document_content": {
      "type": "markdown",
      "markdown": "## Action Items\n\n- [ ] Tyler: Review PR by EOD\n- [ ] Sara: Update Notion"
    }
  }
]'
```

## Tips

- Canvas IDs look like `F0XXXXXXXXX` -- always use `--json` to capture them.
- Channel canvases (`conversations.canvases.create`) are pinned to the channel and visible to all members.
- Standalone canvases must have access explicitly granted.
- The `canvases:write` scope is needed for create/edit/delete; `canvases:read` for sections lookup.
