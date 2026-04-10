---
name: slack-dynamic
description: "The meta-skill: dynamically discover and call ANY of ~250 Slack API methods via the method catalog + raw API passthrough. Use when no other skill covers the task."
command_name: slack-cli
tags: [dynamic, discovery, methods, catalog, api, passthrough, meta, library-card]
---
<!-- installed by slack-cli -->

# /slack-dynamic -- Dynamic Slack API Discovery & Execution

**This is the most important slack-cli skill.** It teaches you how to handle ANY Slack API request, even when no dedicated CLI command or pre-built skill exists. Think of it as the library card for the entire Slack API.

The pattern is always the same three steps:

1. **Search** the method catalog to find the right API method
2. **Read** the method details to understand params, scopes, and token type
3. **Call** the method via the raw API passthrough

## The Three-Step Pattern

### Step 1: Search the method catalog

```bash
slack-cli methods search <keyword>
```

This searches ~250 Slack API methods by name, namespace, description, and parameter names. Returns a ranked list of matches.

Example -- you need to set a channel description:
```bash
slack-cli methods search description
```

Example -- you need to work with user groups:
```bash
slack-cli methods search usergroups
```

Example -- you need to manage reminders:
```bash
slack-cli methods search reminders
```

### Step 2: Get method details

Once you find the right method name, get its full specification:

```bash
slack-cli methods get <method.name>
```

This shows:
- **Description** -- what the method does
- **Required params** -- what you MUST pass
- **Optional params** -- what you CAN pass
- **Param descriptions** -- what each param means
- **Token types** -- whether to use a bot token or user token
- **Required scopes** -- what OAuth scopes the app needs
- **Rate tier** -- how aggressively you can call it (Tier 1-4, Special)
- **Deprecated** flag -- if the method is being phased out
- **Paginated** flag + cursor key -- if the method returns paginated results

### Step 3: Call via API passthrough

```bash
slack-cli api <method.name> --params '{"key": "value", ...}' [--token-type bot|user]
```

- `--params` takes a JSON string of parameters
- `--token-type` defaults to `bot`. Set to `user` if the method requires a user token.
- Always append `--json` for machine-parseable output

## Browsing the Catalog

### List all namespaces

```bash
slack-cli methods namespaces
```

Returns all API namespace groups (e.g., `chat`, `conversations`, `users`, `admin`, `files`, `pins`, `reactions`, `reminders`, `usergroups`, etc.) with method counts.

### List all methods in a namespace

```bash
slack-cli methods list --namespace <namespace>
```

Example:
```bash
slack-cli methods list --namespace admin.conversations
```

This is useful for discovering related methods once you find one that is close to what you need.

### Get catalog stats

```bash
slack-cli methods info
```

Shows total method count, namespace count, and catalog file path.

### Force-refresh the catalog

```bash
slack-cli methods update
```

Re-copies the bundled catalog to the local cache. Use after upgrading `slack-cli`.

## Worked Examples

### Example 1: "Set a channel's description"

**Think:** I need to set a channel description. Let me search for it.

```bash
slack-cli methods search "set topic"
```

Output shows `conversations.setTopic` and `conversations.setPurpose`. The user probably wants "description" which Slack calls "purpose."

```bash
slack-cli methods get conversations.setPurpose
```

Output:
```
Method:       conversations.setPurpose
Description:  Sets the purpose for a conversation
Token Types:  bot, user
Rate Tier:    Tier 3

Required Params:
  channel                  Conversation to set the purpose of
  purpose                  A new, specialer purpose
```

Now call it:
```bash
slack-cli api conversations.setPurpose --params '{"channel": "C0AM2BVMHRT", "purpose": "Team operations and coordination"}'
```

Note: `slack-cli conversations purpose` also exists for this particular method. But the dynamic approach works for ANY method, including ones without dedicated commands.

### Example 2: "Create a reminder for myself"

**Think:** Reminders. Let me search.

```bash
slack-cli methods search reminders
```

Output shows:
- `reminders.add` -- Creates a reminder
- `reminders.complete` -- Marks a reminder as complete
- `reminders.delete` -- Deletes a reminder
- `reminders.info` -- Gets info about a reminder
- `reminders.list` -- Lists all reminders

```bash
slack-cli methods get reminders.add
```

Output:
```
Method:       reminders.add
Description:  Creates a reminder
Token Types:  user
Rate Tier:    Tier 2

Required Params:
  text                     The content of the reminder
  time                     When this reminder should happen (Unix ts, or natural language like "in 15 minutes")

Optional Params:
  user                     The user who will receive the reminder (default: authed user)
```

Note the token type is `user` -- must use `--token-type user`:

```bash
slack-cli api reminders.add --params '{"text": "Review the PR", "time": "in 2 hours"}' --token-type user
```

### Example 3: "List all user groups and their members"

**Think:** User groups. Let me search.

```bash
slack-cli methods search usergroups
```

Output shows several methods. I need `usergroups.list` and `usergroups.users.list`.

```bash
slack-cli methods get usergroups.list
```

Call it:
```bash
slack-cli api usergroups.list --params '{"include_users": true}' --json
```

This returns all user groups with their member lists in one call.

### Example 4: "Set the workspace Do Not Disturb schedule"

**Think:** DND schedule. Let me search.

```bash
slack-cli methods search "do not disturb"
```

Hmm, might not match. Try the namespace approach:

```bash
slack-cli methods search dnd
```

Output shows:
- `dnd.endDnd` -- Ends the current DND session
- `dnd.endSnooze` -- Ends the current snooze
- `dnd.info` -- Retrieves DND status for a user
- `dnd.setSnooze` -- Turns on DND for a set number of minutes
- `dnd.teamInfo` -- Retrieves DND status for up to 50 users

```bash
slack-cli methods get dnd.setSnooze
```

```bash
slack-cli api dnd.setSnooze --params '{"num_minutes": 60}' --token-type user
```

### Example 5: "Get a list of all external shared channels"

**Think:** External/shared channels. Let me browse the admin namespace.

```bash
slack-cli methods search "shared channel"
```

Or browse the namespace:

```bash
slack-cli methods list --namespace admin.conversations
```

Find `admin.conversations.search` and use it:

```bash
slack-cli methods get admin.conversations.search
```

```bash
slack-cli api admin.conversations.search --params '{"query": "", "search_channel_types": "exclude_archived", "connected_team_ids": []}' --token-type user --json
```

### Example 6: "What methods exist for managing apps?"

Pure discovery -- just browse:

```bash
slack-cli methods search apps
```

Then drill into a namespace:

```bash
slack-cli methods list --namespace admin.apps
```

## Token Type Decision Tree

Most methods work with **bot tokens** (the default). Use `--token-type user` when:

1. The method details say `Token Types: user` (not bot)
2. The method is in the `admin.*` namespace (usually requires user token with admin scopes)
3. The method involves personal state: DND, reminders, stars, user profile updates
4. The method is `search.messages` or `search.files` (search requires user token)

When in doubt, check the method details:
```bash
slack-cli methods get METHOD_NAME
```

The `Token Types` line tells you exactly what is supported.

## Handling Paginated Methods

Some methods return paginated results. The method details show:
```
Paginated:    Yes (cursor key: messages)
```

For paginated methods, the first call returns a `response_metadata.next_cursor` field. Pass it back as `cursor` in the next call:

```bash
# First page
slack-cli api conversations.list --params '{"limit": 100}' --json

# Next page (use the cursor from the previous response)
slack-cli api conversations.list --params '{"limit": 100, "cursor": "dXNlcjpVMDYx..."}' --json
```

Note: The dedicated `slack-cli conversations list` command handles pagination automatically. The raw `api` passthrough does not auto-paginate -- you must loop manually.

## Error Handling

- **`method_not_found`** -- The method name is wrong. Double-check with `slack-cli methods search`.
- **`missing_scope`** -- The bot/user token lacks a required scope. Check `slack-cli methods get METHOD` for the required scopes, then update the app's OAuth scopes in the Slack App dashboard.
- **`not_allowed_token_type`** -- You used a bot token for a user-only method (or vice versa). Switch `--token-type`.
- **`invalid_arguments`** -- A required parameter is missing or malformed. Check `slack-cli methods get METHOD` for required params.
- **`ratelimited`** -- You hit the rate limit. The response includes a `Retry-After` header. Wait and retry.

## Tips

- When you are not sure what keyword to search, start broad. `slack-cli methods search channel` returns dozens of results. Scan the list to find the right neighborhood, then use `slack-cli methods list --namespace <ns>` to see everything in that area.
- The method catalog is local (no network calls). Searching and browsing is instant and free.
- Use `slack-cli methods get METHOD --json` to get the method spec as structured JSON for programmatic use.
- If a method is marked `deprecated`, check the description for the replacement method.
- The `slack-cli api` passthrough prints the full Slack API response including error details and `response_metadata`. Always check the `ok` field in the response.
- For complex workflows, chain the dynamic approach: search -> get details -> call -> parse response -> feed into next call. This is how you build multi-step automations on the fly.
