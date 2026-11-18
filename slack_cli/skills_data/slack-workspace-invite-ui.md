---
name: slack-workspace-invite-ui
description: "Invite one person to a Slack workspace through an authorized, already-signed-in admin browser. Requires recipient-specific approval and protected input. Not for channel invites or bulk invitations."
command_name: slack-cli
tags: [slack, workspace, invite, admin, browser, privacy]
---
<!-- installed by slack-cli -->

# /slack-workspace-invite-ui -- One Workspace Invitation

Use the Slack admin UI when the workspace plan does not support the invitation API. This is a browser procedure, not a slack-cli automation command. See [why the UI](https://github.com/8Dvibes/slack-toolkit/blob/main/docs/workspace-invite-ui.md).

## Preconditions and input contract

- The human admin has already signed in to the browser session the agent is authorized to use. Verify the acting account and intended workspace in the UI before reading or writing. Never sign in, sign out, switch identity, extract cookies, or borrow another session.
- Obtain a protected-source reference and record selector for exactly one verified recipient, plus a non-sensitive alias for reporting. Read the email privately from that source; never ask for it pasted into chat, put it in a command argument, or print it in chat, logs, Git, or public artifacts. Keep browser snapshots, screenshots and receipts containing it in approved protected storage; avoid tools that expose it in shared output.
- Sending emails a real person. Require the owner's explicit go for this exact recipient and workspace, bound to the protected record through its alias/selector. A request to install this skill or a general onboarding policy is not send approval. Missing approval means STOP with BLOCKED_OTHER; request approval using the alias only.
- Confirm any identity conflicts, holds, and verified aliases with the protected record. Missing or ambiguous inputs mean STOP. Permission covers one standard Member invitation, with no optional channels.

## Procedure

1. Use the supported browser controls to open the intended workspace's administration area and find invitation management. Inspect the current page and use observed labels and controls; do not rely on saved coordinates or fixed selectors. If browser access is unavailable, stop with BLOCKED_OTHER.
2. Search both **Members** and **Pending invitations** for the exact protected address and any verified aliases required by the identity record. Check complete results, including pagination or filters. An active member means ALREADY_MEMBER; an existing pending invitation means ALREADY_PENDING. Neither authorizes a new send. Ambiguous, deactivated, conflicting, or expired records require owner review: BLOCKED_OTHER. Expiration alone never authorizes a resend.
3. Choose **Invite people** (or its current equivalent) and enter only the one verified address. Select standard **Member** / **coworker**, never guest or administrator. Leave optional channels empty. Do not alter default-channel or workspace settings; do not promise that workspace defaults add no channels. Unexpected role/channel options or defaults that conflict with the approved scope mean STOP.
4. Inspect the final review privately: intended workspace, exact address, one recipient, Member role, and no optional channels. Reconfirm the recipient-specific approval is still applicable. Click **Send once**. Never double-click, retry automatically, send a link, or use an API/token workaround.
5. Perform a **separate readback**: leave the send confirmation and freshly open or refresh Pending invitations. Match the exact address and Member account type. A success toast alone is insufficient. Report SENT_PENDING only when this run submitted once and the independent Pending view confirms it. If the response is ambiguous, inspect Pending without sending again. If the outcome remains uncertain, return BLOCKED_OTHER with `send_attempted: true` and `outcome: uncertain`; do not resend.
6. If the recipient accepted before readback, independently verify active membership and report ALREADY_MEMBER with `send_attempted: true` and a sanitized note that membership was observed after submission. Do not claim the invitation is still pending or that membership proves email delivery.
7. Store any required evidence in approved protected storage: source/approval reference, acting account, workspace, exact-match findings, role, send-attempt flag, observation time in UTC, and expiry if visible. Never copy protected evidence into the public repository. Report only the alias, state, send-attempt flag and sanitized reason. Close only tabs opened for this task; preserve human-owned tabs.

## STOP conditions

- Login, session expiry, 2FA, passkey, or identity mismatch: BLOCKED_AUTH. The human must resolve authentication manually. Never request credentials or attempt authentication. After human resolution, restart identity verification and both dedupe checks.
- Rate limit or invitation throttling: BLOCKED_RATE. Stop; no repeated attempts or alternate identity.
- Billing, upgrade, seat purchase, invitation restrictions, missing permissions, CAPTCHA, identity/hold conflict, missing approval, unexpected UI, or uncertain send: BLOCKED_OTHER. Return a sanitized reason without the address. No bypasses, plan changes, resends, revocations, channel additions, or broader provisioning are authorized.

## Result states

These are reporting conventions, not implemented slack-cli statuses.

| State | Required evidence |
|---|---|
| SENT_PENDING | One submission in this run plus separate exact-match Pending readback as Member. |
| ALREADY_MEMBER | Active membership verified; say whether a send was attempted in this run. |
| ALREADY_PENDING | Pending invitation found before sending; no new send. |
| BLOCKED_AUTH | Authentication or acting-identity boundary prevents continuing. |
| BLOCKED_RATE | Rate limit or invitation throttle observed. |
| BLOCKED_OTHER | Other stop, missing authority, incomplete lookup, or uncertain outcome. |

## Tips

- Workspace admission and channel membership are different operations. This skill authorizes no optional channel additions.
- Pending status does not prove email delivery or acceptance. Preserve uncertainty and never label an old invitation newly sent.
- If privacy-safe browser inspection or protected input handling is unavailable, stop instead of exposing the address.
