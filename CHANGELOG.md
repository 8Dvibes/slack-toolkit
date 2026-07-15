# Changelog

## [0.3.1] - 2026-07-15

### Added

- `slack-cli files download <file_id> [--output PATH]` with `files get` as an alias. The command looks up `url_private_download` through `files.info`, falls back to `url_private`, and uses the Slack filename in the current directory when `--output` is omitted.
- Authenticated, chunked private-file downloads in `SlackClient`. Downloads send the bot bearer token without printing it, keep memory use bounded for large files, and atomically replace the destination only after a successful response.
- Offline download tests covering bearer authentication, chunked streaming, non-200 responses, private URL fallback, default filenames, common Slack errors, and the `files get` alias.

### Changed

- Bundled Slack skills now direct agents to `files download` when they need to read image or document attachments and call out the required `files:read` scope.

## [0.3.0] - 2026-07-11

### Fixed

- **All API calls now default to form encoding (`application/x-www-form-urlencoded`) instead of JSON bodies.** GET-style Web API methods (`conversations.list`, `users.list`, `conversations.history`, ...) only read form-encoded params and silently ignore a JSON body -- `types`, `limit`, `exclude_archived`, and `cursor` were all dropped with no error, so `slack-cli api conversations.list` and `slack-cli conversations list` always returned the default public-only first page. This hid every private channel (real-world miss: #agent-native-os on 2026-07-11). Form encoding is accepted by every Web API method; dict/list params (blocks, attachments) are JSON-serialized into their form field per Slack's documented convention.
- Repaired Slack file upload V2 flow (unreleased fix carried on main)
- `conversations.replies` and `users.lookupByEmail` form-encoding fixes are now subsumed by the form-by-default client

### Added

- `slack-cli api --paginate` (alias `--page-all`): the raw passthrough now follows `response_metadata.next_cursor` until exhausted and merges all pages into one response, using the catalog's `response_key` to locate the paginated list
- `slack-cli api --body-format {form,json}`: explicit escape hatch for methods where a JSON body is specifically desired (default: form)
- Offline regression tests (`tests/test_form_encoding.py`) with a fake Slack that mimics the real silent-drop behavior: JSON bodies are ignored, and a request with `types=private_channel` must surface a private channel

## [0.2.3] - 2026-04-16

### Changed

- Rewrote all 33 skill descriptions for better model selection:
  - Descriptions stay under 230 chars (avoids 252-char truncation in model context windows)
  - Front-loaded trigger phrases for more accurate skill matching
  - Added NOT-clauses to disambiguate overlapping skills (post/schedule, post/block-kit, post/thread, api-expert/dynamic/troubleshooting)
  - CoD-inspired density: informative but concise

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
