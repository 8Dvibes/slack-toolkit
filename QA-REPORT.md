# slack-toolkit v0.2.0 QA Report

Date: 2026-04-13
Build: v0.2.0

## QA Checklist Results

| # | Check | Result |
|---|-------|--------|
| 1 | `slack-cli --version` shows 0.2.0 | PASS |
| 2 | `slack-cli methods search conversations` returns results | PASS |
| 3 | `slack-cli methods get conversations.open` returns method details | PASS |
| 4 | `slack-cli skills list` shows 28 skills in skills_data | PASS |
| 5 | `slack-cli conversations --help` shows all new subcommands | PASS |
| 6 | `slack-cli usergroups --help` works | PASS |
| 7 | `slack-cli canvas --help` works | PASS |
| 8 | `slack-cli reminders --help` works | PASS |
| 9 | `slack-cli dnd --help` works | PASS |
| 10 | `slack-cli docs conversations.open` fetches and caches the doc page | PASS |
| 11 | Every new .py file has no syntax errors | PASS |
| 12 | All 28 skill files exist in skills_data/ | PASS |
| 13 | `slack-cli config show` works without profile configured | PASS |

## Test Suite

```
26 passed in 0.55s
```

All 26 tests pass covering:
- Version check (module + CLI)
- Catalog integrity (306 methods, no duplicates, no stale entries)
- New method presence in catalog
- Module imports (usergroups, canvas, reminders, dnd, docs)
- CLI argument parsing for all new command groups
- Skills count (28) and frontmatter validation
- Docs cache path utilities

## Phase Summary

### Phase 1: Catalog & Docs Engine

**1a. Catalog update**
- Added 41 missing methods to `catalog_data/methods.json`
- Removed 5 stale entries: `entity.present.details`, `team.billingInfo`, `workflows.stepCompleted`, `workflows.stepFailed`, `workflows.updateStep`
- Added correctly named replacements: `entity.presentDetails`, `team.billing.info`
- Final catalog: 306 methods (up from 270)

**1b. `methods update --live` command**
- Added `--live` flag to fetch from `docs.slack.dev` via urllib
- Parses method names from HTML using regex
- Diffs against local catalog, adds new methods, marks deprecated
- Without `--live`, resets to bundled catalog

**1c. `docs` command**
- New `slack_cli/docs.py` module
- Fetches from `https://docs.slack.dev/reference/methods/<name>/`
- Caches in `~/.slack-cli/docs/<method>.md`
- 30-day TTL, `--fresh` flag to bypass
- Parses HTML to extract description, sections, parameter tables

**1d. Staleness check**
- `ensure_catalog()` now checks `~/.slack-cli/methods/meta.json` age
- Prints warning if catalog is >30 days old

### Phase 2: New CLI Commands

**2a. Conversations enhancements**
New subcommands added to `conversations.py` and wired into `cli.py`:
- `open` -- Create DMs/group DMs, auto-resolves emails via `users.lookupByEmail`
- `invite-all` -- Invite all workspace members, with `--dry-run`
- `clone-members` -- Copy members from one channel to another, with `--dry-run`
- `export-members` -- Export as table/csv/json/markdown with name+email
- `diff` -- Compare membership of two channels
- `random` -- Pick random non-bot member
- `inactive` -- List members who haven't posted in N days

**2b. New command modules**
- `slack_cli/usergroups.py` -- 7 commands: create, list, update, disable, enable, members-list, members-update
- `slack_cli/canvas.py` -- 6 commands: create, edit, delete, access-set, access-delete, sections
- `slack_cli/reminders.py` -- 5 commands: add, list, complete, delete, info
- `slack_cli/dnd.py` -- 5 commands: info, set-snooze, end-snooze, end-dnd, team-info

### Phase 3: Skills (13 new)

New skill files created in `skills_data/`:
1. `slack-dm.md` -- DM/group DM creation
2. `slack-identity.md` -- Token verification and scope audit
3. `slack-canvas.md` -- Canvas CRUD
4. `slack-usergroup.md` -- User group management
5. `slack-reminders.md` -- Reminder CRUD
6. `slack-streaming.md` -- AI response streaming via chat.startStream/appendStream/stopStream
7. `slack-assistant.md` -- Slack AI assistant thread management
8. `slack-docs.md` -- Real-time API doc lookup + catalog refresh
9. `slack-lists.md` -- Slack Lists CRUD via api passthrough
10. `slack-dnd.md` -- DND management
11. `slack-admin.md` -- Admin operations subset
12. `slack-calls.md` -- Voice/video call registration
13. `slack-bookmarks.md` -- Channel bookmark management

`slack-bulk-ops.md` updated to include all new bulk operations.

**Total skills: 28** (15 existing + 13 new)

### Phase 4: Packaging

- `pyproject.toml`: version bumped to 0.2.0
- `__init__.py`: `__version__` bumped to 0.2.0
- `tests/test_basic.py`: 26 tests created covering all major functionality
- `slack_cli/skills_data/*.md`: package-data includes all 28 skills

## Key Decisions

- `methods update` without `--live` resets to bundled (offline, reliable). With `--live` it fetches from docs.slack.dev.
- Docs parsing is best-effort HTML scraping with regex -- handles the Docusaurus site structure.
- `invite-all` batches invites in groups of 30 (Slack API limit per call).
- `export-members` makes one `users.info` call per member -- can be slow for large channels.
- `conversations inactive` scans history since cutoff -- limited to 1000 msgs initially.

## Files Changed

- `slack_cli/__init__.py` -- version bump
- `slack_cli/cli.py` -- new handlers + parser entries for all new commands
- `slack_cli/methods.py` -- staleness check, meta.json, live fetch, `--live` flag
- `slack_cli/conversations.py` -- 7 new functions
- `slack_cli/catalog_data/methods.json` -- 306 methods (was 270)
- `pyproject.toml` -- version + description
- **New files:**
  - `slack_cli/usergroups.py`
  - `slack_cli/canvas.py`
  - `slack_cli/reminders.py`
  - `slack_cli/dnd.py`
  - `slack_cli/docs.py`
  - `slack_cli/skills_data/slack-dm.md`
  - `slack_cli/skills_data/slack-identity.md`
  - `slack_cli/skills_data/slack-canvas.md`
  - `slack_cli/skills_data/slack-usergroup.md`
  - `slack_cli/skills_data/slack-reminders.md`
  - `slack_cli/skills_data/slack-streaming.md`
  - `slack_cli/skills_data/slack-assistant.md`
  - `slack_cli/skills_data/slack-docs.md`
  - `slack_cli/skills_data/slack-lists.md`
  - `slack_cli/skills_data/slack-dnd.md`
  - `slack_cli/skills_data/slack-admin.md`
  - `slack_cli/skills_data/slack-calls.md`
  - `slack_cli/skills_data/slack-bookmarks.md`
  - `tests/test_basic.py`
  - `QA-REPORT.md`
