"""Raw Slack API method passthrough.

The escape hatch: call ANY Slack Web API method by name with arbitrary
params, even if slack-cli has no dedicated command for it. Combined
with the method catalog, this gives AI agents full Slack API coverage.
"""

import json
import sys


def call_method(client, method_name, params=None, token_type="bot", as_json=False):
    """Call any Slack API method by name with raw params.

    Args:
        client: A slack_cli.client.SlackClient instance.
        method_name: Slack API method name (e.g. "chat.postMessage").
        params: Dict of params to pass to the method.
        token_type: "bot" or "user" -- which token to authenticate with.
        as_json: If True, print raw JSON to stdout.

    Returns:
        The parsed response dict.
    """
    result = client.call(method_name, params=params, token_type=token_type)

    if not result.get("ok"):
        error = result.get("error", "unknown_error")
        print(f"Error: {error}", file=sys.stderr)
        if result.get("response_metadata", {}).get("messages"):
            for msg in result["response_metadata"]["messages"]:
                print(f"  {msg}", file=sys.stderr)

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))

    return result
