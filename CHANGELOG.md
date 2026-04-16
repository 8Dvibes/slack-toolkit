# Changelog

## [0.2.2] - 2026-04-16

### Added

- 5 expert skills for dynamic agent usage (Layer 2):
  - `slack-api-expert`: master guide with self-service resolution chain, token types, pagination, rate limits, opensrc-style source reading
  - `slack-block-kit`: rich message building with 5 ready-to-use Block Kit templates
  - `slack-integration-patterns`: 6 architectural patterns for agent-to-Slack workflows
  - `slack-mrkdwn`: complete Slack markup syntax reference with markdown comparison
  - `slack-troubleshooting`: self-diagnosis guide for 15 common API errors
- Enhanced `slack-dynamic` skill with full resolution chain and source reading patterns

### Changed

- Total bundled skills: 28 → 33
- README updated with expert skills in catalog table
- Blueprint updated to reflect v0.2.2

## [0.2.0] - 2026-04-15

### Added

- Methods update command with live docs.slack.dev scraping (`slack-cli methods update --live`)
- Per-method documentation fetch and cache (`slack-cli docs <method>`) -- caches to `~/.slack-cli/docs/` with 30-day TTL
- Catalog staleness detection: warns if the catalog is older than 30 days
- `conversations open` -- create DMs and group DMs, auto-resolves emails to user IDs
- `conversations invite-all` -- invite all workspace members to a channel (with `--dry-run`)
- `conversations clone-members` -- copy membership from one channel to another (with `--dry-run`)
- `conversations export-members` -- export member list as table, CSV, JSON, or Markdown
- `conversations diff` -- compare membership of two channels
- `conversations random` -- pick a random non-bot member from a channel
- `conversations inactive` -- list members who haven't posted in N days
- New command module: `usergroups` (create, list, update, disable, enable, members list, members update)
- New command module: `canvas` (create, edit, delete, access set, access delete, sections)
- New command module: `reminders` (add, list, complete, delete, info)
- New command module: `dnd` (info, set-snooze, end-snooze, end-dnd, team-info)
- 13 new skills: `slack-dm`, `slack-identity`, `slack-canvas`, `slack-usergroup`, `slack-reminders`, `slack-streaming`, `slack-assistant`, `slack-docs`, `slack-lists`, `slack-dnd`, `slack-admin`, `slack-calls`, `slack-bookmarks`
- `slack-bulk-ops` skill updated to cover all new bulk conversation operations
- Catalog expanded from 270 to 306 methods (41 new methods added)
- 5 stale/deprecated methods removed from catalog

### Fixed

- `entity.present.details` renamed to `entity.presentDetails` in catalog
- `team.billingInfo` renamed to `team.billing.info` in catalog

## [0.1.0] - 2026-04-10

### Added

- Initial release: zero-dependency Slack Web API CLI (Python stdlib only)
- 270-method catalog with search, get, list, and namespaces commands
- 10 command groups: chat, conversations, users, search, files, reactions, pins, bookmarks, api, methods
- 15 Claude Code skills with install system (`slack-cli skills install`)
- Profile-based configuration (`~/.slack-cli.json`) with env-var overrides
- Auto-pagination via `client.paginate()` for all list endpoints
- Rate-limit retry with exponential backoff on 429 responses
- Raw API passthrough (`slack-cli api <method>`) for any Slack Web API method
- File upload using the V2 two-step flow (get upload URL, upload bytes, complete)
