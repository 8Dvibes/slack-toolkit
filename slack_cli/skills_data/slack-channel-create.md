---
name: slack-channel-create
description: "Create Slack channels with full setup: name, public/private, topic, purpose, invite members, add bookmarks. One-shot channel provisioning."
command_name: slack-cli
tags: [slack, channel, create, setup, onboarding]
---
<!-- installed by slack-cli -->

# /slack-channel-create -- Create and Fully Set Up a Slack Channel

Create a new Slack channel and configure it in one pass: name, visibility, topic, purpose, members, and bookmarks.

## When to Use

- Spinning up a new project channel
- Creating a channel for a new cohort, team, or workstream
- Setting up a channel with all metadata from a single request
- Automating channel provisioning as part of onboarding

## Procedure

### Step 1: Create the Channel

Public channel:

```bash
slack-cli conversations create "project-alpha"
```

Private channel:

```bash
slack-cli conversations create "project-alpha-internal" --private
```

Use `--json` to capture the channel ID from the response:

```bash
slack-cli conversations create "project-alpha" --json
```

The response includes the new channel object with its `id` (e.g., `C0XXXXXXXXX`). Save this ID for the following steps.

**Channel naming rules:**
- Lowercase only, no spaces
- Hyphens and underscores are allowed
- Max 80 characters
- Must be unique in the workspace

### Step 2: Set the Topic

The topic appears at the top of the channel and in the channel header:

```bash
slack-cli conversations topic <CHANNEL_ID> "Active sprint: Project Alpha v2 launch"
```

Keep topics short and actionable. They are visible at a glance.

### Step 3: Set the Purpose

The purpose appears in the channel details sidebar and in channel search results:

```bash
slack-cli conversations purpose <CHANNEL_ID> "Coordination channel for the Project Alpha v2 launch. All design, dev, and QA updates go here."
```

The purpose can be longer and more descriptive than the topic.

### Step 4: Invite Members

Invite users by their user IDs (comma-separated for multiple):

```bash
slack-cli conversations invite <CHANNEL_ID> U07MBKFRLAG,U07M6QW8DML,U07MV3K3203
```

If you have emails instead of user IDs, look them up first:

```bash
slack-cli users lookup tyler@example.com --json
```

The response includes the `user.id` field.

To invite a large number of users, you can batch them in groups (Slack accepts up to 1000 per call, but smaller batches are safer):

```bash
slack-cli conversations invite <CHANNEL_ID> U001,U002,U003,U004,U005
```

### Step 5: Add Bookmarks (Optional)

Bookmarks appear as links at the top of the channel, below the topic:

```bash
slack-cli bookmarks add <CHANNEL_ID> "Project Brief" "https://docs.google.com/document/d/abc123"
```

With an emoji icon:

```bash
slack-cli bookmarks add <CHANNEL_ID> "Sprint Board" "https://linear.app/team/board" --emoji ":dart:"
```

Add multiple bookmarks:

```bash
slack-cli bookmarks add <CHANNEL_ID> "Design Spec" "https://figma.com/file/xyz"
slack-cli bookmarks add <CHANNEL_ID> "Repo" "https://github.com/org/project-alpha" --emoji ":octocat:"
slack-cli bookmarks add <CHANNEL_ID> "Slack Archive" "https://example.com/archive" --emoji ":floppy_disk:"
```

### Step 6: Post a Welcome Message (Optional)

```bash
slack-cli chat post <CHANNEL_ID> "Welcome to #project-alpha! Check the bookmarks above for key links. Topic has the current sprint focus."
```

Or with Block Kit for richer formatting:

```bash
slack-cli chat post <CHANNEL_ID> "Welcome to the channel" --blocks '[{"type":"section","text":{"type":"mrkdwn","text":"*Welcome to #project-alpha!*\n\nKey resources:\n- <https://docs.google.com/document/d/abc123|Project Brief>\n- <https://github.com/org/project-alpha|GitHub Repo>\n\nCurrent focus: v2 launch prep"}}]'
```

## Full Example: One-Shot Channel Setup

```bash
# Create the channel and capture the ID
CHANNEL_ID=$(slack-cli conversations create "docgen-c8" --json | python3 -c "import sys,json; print(json.load(sys.stdin)['channel']['id'])")

# Configure metadata
slack-cli conversations topic "$CHANNEL_ID" "DocGen Cohort 8 - Week 1"
slack-cli conversations purpose "$CHANNEL_ID" "Coordination channel for DocGen Cohort 8. Assignments, Q&A, and build updates."

# Invite members
slack-cli conversations invite "$CHANNEL_ID" U07MBKFRLAG,U07M6QW8DML

# Add bookmarks
slack-cli bookmarks add "$CHANNEL_ID" "Curriculum" "https://notion.so/curriculum-c8" --emoji ":books:"
slack-cli bookmarks add "$CHANNEL_ID" "Submissions" "https://forms.google.com/c8-submit" --emoji ":inbox_tray:"

# Post welcome message
slack-cli chat post "$CHANNEL_ID" "Channel is live! Check the bookmarks for curriculum and submission links."

echo "Done: $CHANNEL_ID"
```

## Managing an Existing Channel

### List bookmarks

```bash
slack-cli bookmarks list <CHANNEL_ID>
```

### Edit a bookmark

```bash
slack-cli bookmarks edit <CHANNEL_ID> <BOOKMARK_ID> --title "Updated Title" --link "https://new-url.com"
```

### Remove a bookmark

```bash
slack-cli bookmarks remove <CHANNEL_ID> <BOOKMARK_ID>
```

### Remove a member

```bash
slack-cli conversations kick <CHANNEL_ID> <USER_ID>
```

### Archive the channel when done

```bash
slack-cli conversations archive <CHANNEL_ID>
```

## Tips

- The bot must be a member of the channel to set topic, purpose, add bookmarks, or invite users. The bot is automatically added as a member when it creates the channel.
- Private channels cannot be converted to public (or vice versa) after creation. Choose carefully.
- If `conversations create` fails with `name_taken`, the channel name already exists. Check for archived channels with that name -- Slack reserves names even for archived channels.
- Bookmark emoji must include colons (e.g., `":rocket:"` not `"rocket"`).
- The `conversations invite` command requires the bot to have the `channels:manage` (public) or `groups:write` (private) scope.
- To create a channel on a different workspace, use `--profile <name>` to select the appropriate config profile.
