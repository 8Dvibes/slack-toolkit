# Pre-post guard

A profile can name a command array in `pre_post_guard`. Before
`chat.postMessage`, `chat.scheduleMessage`, or `chat.update` reaches HTTP, the
client passes `{method, params}` as JSON on stdin to that command. This covers
the dedicated immediate/queued commands and raw `api` calls through this client.
The command must exit zero and return `{"verdict":"PASS"}`; missing programs,
invalid output, HOLD, and timeouts stop the write with a fixed error code.
Hook stdout/stderr are not echoed. Credentials are not included in the payload.
Read-only methods do not invoke it. Other profiles are unchanged.

Configure without changing credentials:

```
slack-cli config set-profile gigawatt --pre-post-guard '["python3","/absolute/path/to/slack_verify.py","check"]'
```

AI Build Lab uses the existing Founders Lounge `zoom_room_guard.check_draft`
via its `slack_verify.py check` adapter. Set `AIBL_ZOOM_SERIES` to a JSON array
of registry series IDs and `AIBL_LEARN_ROUTES_FILE` to the existing fresh
verified Learn-routes export when needed. The shared verified writer supplies
series context automatically. Missing evidence holds student-room writes.
Verified staff-only channels are exempt from student-room checks. A post that
names no series is judged on rooms only: ordinary links and plain numbers pass,
and any Zoom link, Maven join link, Learn session link, shortener or stated
meeting number still holds. A post with a named series gets the full check.

This is a profile-configured CLI/client guard, not interception of arbitrary
HTTP clients, another machine's unsynchronized installation, or Slack itself.
