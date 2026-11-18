# Why workspace invitations use the admin UI

Slack's [admin.users.invite documentation](https://docs.slack.dev/reference/methods/admin.users.invite/) states: “The features within are only available to Slack workspaces on an Enterprise plan.” It lists a user token with the `admin.users:write` scope. A bot token or a non-Enterprise plan does not gain this capability by using the raw API passthrough.

Verified on 2026-11-18: `slack-cli docs admin.users.invite --fresh` fetched the official page, but its extracted output omitted the plan restriction. The restriction and user-token scope were verified directly in the official page's HTML. Recheck that source when plan support changes; an incomplete CLI extraction is not evidence that all plans are supported.

For an authorized workspace without this API capability, use the bundled `slack-workspace-invite-ui` skill with a human-admin-signed-in browser. It requires explicit approval for one protected recipient, Members and Pending deduplication, standard Member role, no optional channels, one send, and separate Pending readback. It stops at authentication, rate-limit, billing, and other authority boundaries. It adds no browser automation code or invite command to slack-cli.
