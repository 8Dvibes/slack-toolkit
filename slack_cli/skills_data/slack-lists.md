---
name: slack-lists
description: "Manage Slack Lists (native task/kanban feature). CRUD operations on lists and items via API passthrough. Use when creating, updating, or querying Slack Lists."
command_name: slack-cli
tags: [slack, lists, items, tasks, kanban, crud]
---
<!-- installed by slack-cli -->

# /slack-lists -- Slack Lists Management

Create and manage Slack Lists and their items via the `slack-cli api` passthrough.

## Required Scope

Bot token needs: `lists:write` (create/update/delete), `lists:read` (read)

## API Methods Used (via slack-cli api passthrough)

- `slackLists.create` -- Create a new list
- `slackLists.update` -- Update a list
- `slackLists.items.create` -- Add an item to a list
- `slackLists.items.update` -- Update a list item
- `slackLists.items.delete` -- Delete a list item
- `slackLists.items.deleteMultiple` -- Bulk delete list items
- `slackLists.items.info` -- Get item details
- `slackLists.items.list` -- List all items in a list
- `slackLists.access.set` -- Set list access
- `slackLists.access.delete` -- Revoke list access
- `slackLists.download.start` / `slackLists.download.get` -- Export list as CSV

## Procedure

### Step 1: Create a list

```bash
slack-cli api slackLists.create --params '{
  "name": "Sprint Tasks",
  "channel_id": "C08ACMRDC04"
}' --json
```

### Step 2: Add items to a list

```bash
slack-cli api slackLists.items.create --params '{
  "list_id": "LIST_ID_HERE",
  "column_values": [
    {"column_id": "title", "value": "Build streaming feature"},
    {"column_id": "assignee", "value": "U07MBKFRLAG"},
    {"column_id": "status", "value": "In Progress"}
  ]
}' --json
```

### Step 3: List all items

```bash
slack-cli api slackLists.items.list --params '{
  "list_id": "LIST_ID_HERE"
}' --json
```

### Step 4: Update an item

```bash
slack-cli api slackLists.items.update --params '{
  "list_id": "LIST_ID_HERE",
  "item_id": "ITEM_ID_HERE",
  "column_values": [
    {"column_id": "status", "value": "Done"}
  ]
}' --json
```

### Step 5: Delete items

```bash
# Single item
slack-cli api slackLists.items.delete --params '{
  "list_id": "LIST_ID_HERE",
  "item_id": "ITEM_ID_HERE"
}'

# Multiple items
slack-cli api slackLists.items.deleteMultiple --params '{
  "list_id": "LIST_ID_HERE",
  "item_ids": ["ITEM_1", "ITEM_2", "ITEM_3"]
}'
```

### Step 6: Export a list as CSV

```bash
# Start export
slack-cli api slackLists.download.start --params '{
  "list_id": "LIST_ID_HERE"
}' --json
# Returns download_id

# Get the download
slack-cli api slackLists.download.get --params '{
  "download_id": "DOWNLOAD_ID_HERE"
}' --json
```

## Manage Access

```bash
# Grant access
slack-cli api slackLists.access.set --params '{
  "list_id": "LIST_ID_HERE",
  "access_level": "write",
  "user_ids": ["U07MBKFRLAG"]
}'

# Revoke access
slack-cli api slackLists.access.delete --params '{
  "list_id": "LIST_ID_HERE",
  "user_ids": ["U07MBKFRLAG"]
}'
```

## Tips

- List IDs and item IDs are returned in the API response -- always use `--json` to capture them.
- Column IDs depend on your list schema -- use `slackLists.items.list` to discover column IDs.
- Slack Lists is a newer feature -- ensure your bot has the `lists:write` scope.
- For large exports, poll `slackLists.download.get` until `status` is `complete`.
