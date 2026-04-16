---
name: slack-reactions
description: "Add, remove, and audit emoji reactions on Slack messages. Build lightweight polls with reaction-based voting. NOT for listing custom emoji (/slack-emoji). Use when reacting to a message or running a reaction poll."
command_name: slack-cli
tags: [reactions, emoji, polls, voting, engagement]
---
<!-- installed by slack-cli -->

# /slack-reactions -- Emoji Reactions & Reaction-Based Polls

Add, remove, inspect, and audit emoji reactions on Slack messages. Build lightweight poll/voting flows using reactions.

## Core Commands

### Add a reaction

```bash
slack-cli reactions add CHANNEL_ID MESSAGE_TS EMOJI_NAME
```

- `CHANNEL_ID` -- the channel containing the message (e.g., `C0AM2BVMHRT`)
- `MESSAGE_TS` -- the message timestamp (e.g., `1712764800.123456`)
- `EMOJI_NAME` -- emoji name WITHOUT colons (e.g., `thumbsup` not `:thumbsup:`)

Example:
```bash
slack-cli reactions add C0AM2BVMHRT 1712764800.123456 white_check_mark
```

### Remove a reaction

```bash
slack-cli reactions remove CHANNEL_ID MESSAGE_TS EMOJI_NAME
```

Example:
```bash
slack-cli reactions remove C0AM2BVMHRT 1712764800.123456 white_check_mark
```

### Get reactions on a specific message

```bash
slack-cli reactions get CHANNEL_ID MESSAGE_TS
```

With JSON output for programmatic parsing:
```bash
slack-cli reactions get CHANNEL_ID MESSAGE_TS --json
```

Returns a list of reactions with name, count, and user IDs of who reacted.

### List reactions by a user

```bash
slack-cli reactions list --user USER_ID --count 50
```

If `--user` is omitted, lists reactions by the authenticated bot user.

With JSON:
```bash
slack-cli reactions list --user USER_ID --json
```

## Procedures

### Procedure 1: Audit reactions on a message

Use this to see who reacted with what on a specific message.

```bash
slack-cli reactions get CHANNEL_ID MESSAGE_TS --json
```

Parse the response to build a summary:

```
## Reactions on message 1712764800.123456

| Emoji | Count | Users |
|-------|-------|-------|
| :thumbsup: | 5 | Tyler, Sara, Wade, +2 more |
| :eyes: | 2 | Tyler, Sara |
| :rocket: | 1 | Wade |

Total: 8 reactions from 3 unique users
```

To resolve user IDs to names, cross-reference with:
```bash
slack-cli users info USER_ID --json
```

### Procedure 2: Audit reaction patterns across a channel

Scan recent messages in a channel to find the most-reacted-to messages and most-used emoji.

1. Pull message history:
   ```bash
   slack-cli conversations history CHANNEL_ID --limit 100 --json
   ```

2. For each message that has a `reactions` field in the JSON, tally:
   - Total reaction count per message
   - Most common emoji across all messages
   - Most-reacted-to messages (ranked by total reaction count)

3. Present findings:
   ```
   ## Reaction Audit -- #gigawatt-lounge -- Last 100 messages

   ### Most reacted-to messages
   | Message (preview) | Timestamp | Total Reactions | Top Emoji |
   |-------------------|-----------|-----------------|-----------|
   | "Shipped the new dashboard..." | 1712764800.123 | 12 | :rocket: (5), :fire: (4) |
   | "Q2 numbers are in..." | 1712678400.456 | 8 | :chart_with_upwards_trend: (6) |

   ### Most used emoji (across 100 messages)
   | Emoji | Total Uses |
   |-------|-----------|
   | :thumbsup: | 34 |
   | :eyes: | 21 |
   | :rocket: | 15 |

   ### Engagement stats
   - Messages with at least 1 reaction: 42/100 (42%)
   - Average reactions per reacted message: 3.2
   - Unique emoji used: 18
   ```

### Procedure 3: Poll-style voting with reactions

Create a lightweight poll by posting a message and seeding it with reaction options.

1. **Post the poll message:**
   ```bash
   slack-cli chat post CHANNEL_ID "Poll: When should we hold the all-hands?\n\n:one: Monday 2pm\n:two: Tuesday 10am\n:three: Wednesday 3pm\n\nReact to vote!"
   ```

2. **Capture the message timestamp** from the response (the `ts` field).

3. **Seed the reactions** so users know which emoji to click:
   ```bash
   slack-cli reactions add CHANNEL_ID MESSAGE_TS one
   slack-cli reactions add CHANNEL_ID MESSAGE_TS two
   slack-cli reactions add CHANNEL_ID MESSAGE_TS three
   ```

4. **Check results later:**
   ```bash
   slack-cli reactions get CHANNEL_ID MESSAGE_TS --json
   ```

5. **Tally and report:**
   ```
   ## Poll Results: All-hands timing

   :one: Monday 2pm -- 3 votes (Tyler, Sara, Wade)
   :two: Tuesday 10am -- 7 votes (winner!)
   :three: Wednesday 3pm -- 2 votes

   Total votes: 12
   Winner: Tuesday 10am (:two:) with 7 votes
   ```

   Note: Subtract 1 from each count to exclude the bot's seed reaction, unless the bot's vote should count.

### Procedure 4: React to confirm/acknowledge

Use reactions as lightweight acknowledgment signals:

**Mark a message as "seen":**
```bash
slack-cli reactions add CHANNEL_ID MESSAGE_TS eyes
```

**Mark a message as "done":**
```bash
slack-cli reactions add CHANNEL_ID MESSAGE_TS white_check_mark
```

**Mark a message as "needs attention":**
```bash
slack-cli reactions add CHANNEL_ID MESSAGE_TS rotating_light
```

## Common Emoji Names (without colons)

| Emoji | Name to use |
|-------|-------------|
| +1 | `thumbsup` |
| -1 | `thumbsdown` |
| Check mark | `white_check_mark` |
| Eyes | `eyes` |
| Rocket | `rocket` |
| Fire | `fire` |
| Heart | `heart` |
| Wave | `wave` |
| Party | `tada` |
| Warning | `warning` |
| Red circle | `red_circle` |
| Numbers 1-9 | `one`, `two`, `three`, etc. |

## Error Handling

- **`already_reacted`** -- The bot already reacted with this emoji. Safe to ignore.
- **`no_reaction`** -- Tried to remove a reaction the bot hasn't added. Safe to ignore.
- **`message_not_found`** -- The message timestamp is wrong or the message was deleted. Verify the `ts` value.
- **`channel_not_found`** -- The channel ID is wrong or the bot is not in the channel. Check with `slack-cli conversations list`.
- **`invalid_name`** -- The emoji name is wrong. Custom emoji names are case-sensitive. Use `slack-cli api emoji.list --json` to verify custom emoji names.

## Tips

- Emoji names never include colons in the CLI. Use `thumbsup`, not `:thumbsup:`.
- The `reactions get` command returns user IDs, not display names. Use `slack-cli users info USER_ID` to resolve names when presenting results to humans.
- For polls, always seed reactions immediately after posting. This makes the voting options visually obvious to users.
- The `reactions list` command (list reactions by a user) is rate-limited at Tier 2 (~20/min). The per-message `reactions get` is Tier 3 (~50/min).
- Thread messages have their own timestamps. To react to a thread reply, use the reply's `ts`, not the parent's `ts`. The channel ID stays the same.
- A message can have at most 23 different emoji reactions (Slack platform limit).
