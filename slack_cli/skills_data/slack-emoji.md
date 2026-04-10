---
name: slack-emoji
description: "List and search custom emoji in the workspace. Uses the raw API passthrough since there is no dedicated emoji command. Demonstrates the method catalog + api passthrough pattern."
command_name: slack-cli
tags: [emoji, custom, api, passthrough, methods]
---
<!-- installed by slack-cli -->

# /slack-emoji -- Custom Emoji Management

List, search, and inspect custom emoji in the Slack workspace. Since `slack-cli` has no dedicated emoji subcommand, this skill uses the **method catalog + raw API passthrough** pattern -- the same approach the `/slack-dynamic` skill teaches for any uncovered API method.

## How It Works (the Pattern)

This skill is also a teaching example of how to use `slack-cli` for API methods that do not have a dedicated CLI command.

### Step 1: Discover the method

```bash
slack-cli methods search emoji
```

This returns methods like:
- `emoji.list` -- Lists custom emoji for a team

### Step 2: Get method details

```bash
slack-cli methods get emoji.list
```

This shows:
- Required/optional params
- Token type (bot or user)
- Required scopes
- Rate tier

### Step 3: Call via API passthrough

```bash
slack-cli api emoji.list --json
```

The `api` subcommand is the escape hatch -- it calls any Slack API method by name, passing params as JSON.

## Procedure

### List all custom emoji

```bash
slack-cli api emoji.list --json
```

The response contains an `emoji` object where keys are emoji names and values are either:
- A URL to the image (for custom-uploaded emoji)
- `alias:other_name` (for emoji aliases)

### Search for a specific emoji

There is no server-side search for emoji. Pull the full list and filter locally:

```bash
slack-cli api emoji.list --json
```

Then parse the JSON `emoji` object and filter keys matching the search term. For example, to find all emoji containing "party":

```bash
slack-cli api emoji.list --json | jq '.emoji | to_entries[] | select(.key | contains("party"))'
```

### Count custom emoji

```bash
slack-cli api emoji.list --json | jq '.emoji | length'
```

### Find emoji aliases

Aliases have values starting with `alias:`. To list all aliases:

```bash
slack-cli api emoji.list --json | jq '.emoji | to_entries[] | select(.value | startswith("alias:"))'
```

### Check if a specific emoji exists

```bash
slack-cli api emoji.list --json | jq '.emoji["emoji-name"] // "not found"'
```

## Output Format

When presenting emoji results to the user:

```
## Custom Emoji -- [workspace name]

Total custom emoji: 247 (including 31 aliases)

### Search results for "party"
| Name | Type | Value |
|------|------|-------|
| :partyparrot: | image | https://emoji.slack-edge.com/T.../partyparrot/abc123.gif |
| :party-blob: | image | https://emoji.slack-edge.com/T.../party-blob/def456.png |
| :party: | alias | alias:tada |

### Top-level stats
- Custom images: 216
- Aliases: 31
```

## Worked Examples

### Example 1: "What custom emoji do we have?"

```bash
slack-cli api emoji.list --json
```

Parse the response and present a summary: total count, a sample of 10-20 popular ones, and the alias count.

### Example 2: "Do we have a :shipit: emoji?"

```bash
slack-cli api emoji.list --json | jq '.emoji["shipit"] // "not found"'
```

If the value is a URL, the emoji exists. If it starts with `alias:`, tell the user it is an alias. If `"not found"`, it does not exist.

### Example 3: "Show me all our animated emoji"

Pull the full list, then filter for URLs ending in `.gif`:

```bash
slack-cli api emoji.list --json | jq '[.emoji | to_entries[] | select(.value | endswith(".gif"))] | length'
```

## Token Type Notes

- `emoji.list` works with **bot tokens** -- no user token needed
- The required scope is `emoji:read`
- Rate tier is Tier 2 (~20 requests per minute), but you typically only need one call since the full list comes back in a single response

## Tips

- The emoji list can be large (hundreds or thousands of entries). Always use `--json` and parse programmatically rather than eyeballing raw output.
- Slack's built-in emoji (like `:thumbsup:`) are NOT returned by `emoji.list` -- only custom workspace emoji appear.
- If the user asks to upload or add a new emoji, that requires the `admin.emoji.add` method, which is only available on Enterprise Grid plans. Let the user know if they ask.
- To check who added an emoji, you would need `admin.emoji.list` (Enterprise Grid only). The standard `emoji.list` does not include creator info.
