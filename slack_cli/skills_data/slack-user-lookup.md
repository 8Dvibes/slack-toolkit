---
name: slack-user-lookup
description: "Look up Slack users by email, ID, or name. Show profile details, presence status, and recent activity. Use when identifying users, checking availability, or building user context."
command_name: slack-cli
tags: [slack, users, lookup, profile, presence, email]
---
<!-- installed by slack-cli -->

# /slack-user-lookup -- Slack User Lookup

Find and inspect Slack users by email address, user ID, or browsing the user list.

## Arguments

- `/slack-user-lookup <email>` -- Look up a user by email
- `/slack-user-lookup <user_id>` -- Look up a user by Slack ID
- `/slack-user-lookup` -- Browse all workspace users

## Procedure

### Step 1: Look Up by Email

The fastest way to find a specific user:

```bash
slack-cli users lookup tyler@aibuildlab.com --json
```

This returns the full user object including their user ID, display name, and profile.

### Step 2: Look Up by User ID

If you already have a user ID (e.g., from a message or channel member list):

```bash
slack-cli users info U07MBKFRLAG --json
```

Key fields in the response:

- `user.id` -- Slack user ID
- `user.name` -- username (login name)
- `user.real_name` -- full display name
- `user.is_admin` -- workspace admin flag
- `user.is_owner` -- workspace owner flag
- `user.is_bot` -- whether this is a bot user
- `user.deleted` -- whether the account is deactivated
- `user.tz` -- timezone string
- `user.tz_offset` -- UTC offset in seconds

### Step 3: Get Full Profile

For detailed profile information (title, phone, custom fields):

```bash
slack-cli users profile U07MBKFRLAG --json
```

Profile fields:

- `profile.title` -- job title
- `profile.phone` -- phone number
- `profile.email` -- email address
- `profile.display_name` -- preferred display name
- `profile.status_text` -- custom status text
- `profile.status_emoji` -- custom status emoji
- `profile.image_512` -- profile photo URL
- `profile.first_name` / `profile.last_name` -- name components

### Step 4: Check Presence

See if a user is currently active:

```bash
slack-cli users presence U07MBKFRLAG --json
```

Returns:

- `presence` -- `active` or `away`
- `online` -- boolean
- `auto_away` -- whether Slack auto-set them as away
- `connection_count` -- number of active clients (desktop, mobile, etc.)

### Step 5: Browse All Users

List all users in the workspace:

```bash
# Default list
slack-cli users list

# JSON output with limit
slack-cli users list --limit 100 --json
```

To find a user by name when you do not have their email or ID, list all users and search the output:

```bash
slack-cli users list --json
```

Then filter the JSON for the name you are looking for.

## Output Format

```
## User Profile: Tyler Fisk

**User ID:** U07MBKFRLAG
**Username:** tyler
**Display Name:** Tyler Fisk
**Email:** tyler@aibuildlab.com
**Title:** Founder
**Timezone:** America/Chicago (CST)

### Status
- Presence: Active
- Custom Status: :rocket: Building things
- Online Clients: 2

### Account
- Admin: Yes
- Owner: Yes
- Bot: No
- Deactivated: No
```

## Common Workflows

### Resolve a User ID from a Message

When you see a user ID in a message (e.g., `<@U07MBKFRLAG>`), look it up:

```bash
slack-cli users info U07MBKFRLAG --json
```

### Find Someone's Slack ID from Email

Useful for inviting users to channels or sending DMs:

```bash
# Get the user ID
slack-cli users lookup sara@aibuildlab.com --json

# Then invite them to a channel
slack-cli conversations invite <channel> <user_id>
```

### Check if Someone is Online Before Messaging

```bash
slack-cli users presence U07MBKFRLAG --json
```

If they are `away`, consider scheduling the message instead of posting immediately:

```bash
# Schedule for when they are likely online
slack-cli chat schedule <channel> "Hey, when you're back..." <future_unix_ts>
```

### List All Bots in the Workspace

```bash
slack-cli users list --json
```

Then filter for entries where `is_bot` is `true`.

### Build a User Directory

```bash
slack-cli users list --limit 200 --json
```

Extract `id`, `real_name`, `profile.email`, and `profile.title` for each user to build a lookup table.

## Tips

- **Email lookup is exact match only.** The email must match exactly what is in the user's Slack profile. No partial matching or wildcards.
- **Deactivated users still appear.** Users with `deleted: true` are deactivated accounts. They show up in `users list` and `users info` but cannot post or be messaged.
- **Bot users have separate IDs.** A Slack app has both a bot user ID (`U...`) and a bot ID (`B...`). The user ID is what appears in messages and member lists.
- **Presence may be stale.** Slack presence updates are not real-time through the API. A user may show as `active` for several minutes after going idle.
- **Rate limits.** `users.info` and `users.list` are Tier 2 (~20 requests/min). Avoid looking up every user ID in a large channel one by one. Use `users list` to fetch in bulk instead.
- **Display name vs. real name.** `display_name` is what the user chose to show in Slack. `real_name` is from their profile/SSO. They may differ.
- **Guest accounts.** Multi-channel guests and single-channel guests have `is_restricted` or `is_ultra_restricted` set to `true`.
