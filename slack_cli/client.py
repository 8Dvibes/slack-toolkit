"""HTTP client for the Slack Web API. Zero external dependencies (urllib only)."""

import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

# Maximum retries on 429 rate-limit responses
_MAX_RETRIES = 5


class SlackApiError(Exception):
    """Raised when the Slack API returns ok=false or an HTTP error."""

    def __init__(self, error: str, status: int = 200, body: Any = None):
        self.error = error
        self.status = status
        self.body = body
        super().__init__(f"Slack API error: {error}")


class SlackClient:
    """Low-level REST client for the Slack Web API."""

    BASE_URL = "https://slack.com/api/"

    def __init__(self, bot_token: str, user_token: Optional[str] = None):
        self.bot_token = bot_token
        self.user_token = user_token
        self._ctx = ssl.create_default_context()

    def _get_token(self, token_type: str = "bot") -> str:
        """Resolve which token to use."""
        if token_type == "user":
            if not self.user_token:
                raise SlackApiError(
                    "User token (xoxp-) required but not configured. "
                    "Set --user-token in your profile or SLACK_USER_TOKEN env var."
                )
            return self.user_token
        if token_type == "auto":
            # Prefer bot, fall back to user
            return self.bot_token or self.user_token or ""
        # Default: bot
        return self.bot_token

    def _request(
        self,
        method_name: str,
        params: Optional[dict] = None,
        token_type: str = "bot",
    ) -> dict:
        """POST to https://slack.com/api/{method_name} with JSON body.

        Handles rate limiting with exponential backoff + jitter.
        Returns the parsed JSON response dict.
        """
        import random

        url = f"{self.BASE_URL}{method_name}"
        token = self._get_token(token_type)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        data = json.dumps(params or {}).encode("utf-8")

        for attempt in range(_MAX_RETRIES + 1):
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            try:
                with urllib.request.urlopen(req, context=self._ctx, timeout=30) as resp:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < _MAX_RETRIES:
                    # Rate limited -- respect Retry-After header
                    retry_after = int(e.headers.get("Retry-After", "1"))
                    # Exponential backoff with jitter
                    wait = retry_after + (random.random() * (2 ** attempt))
                    print(
                        f"Rate limited. Retrying in {wait:.1f}s (attempt {attempt + 1}/{_MAX_RETRIES})...",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue

                body_text = ""
                try:
                    body_text = e.read().decode("utf-8")
                    err_body = json.loads(body_text)
                except Exception:
                    err_body = body_text

                msg = body_text
                if isinstance(err_body, dict):
                    msg = err_body.get("error", body_text)

                raise SlackApiError(msg, status=e.code, body=err_body) from e
            except urllib.error.URLError as e:
                print(f"Connection error: {e.reason}", file=sys.stderr)
                sys.exit(1)

        # Exhausted retries
        raise SlackApiError("Rate limit retries exhausted", status=429)

    def call(
        self,
        method_name: str,
        params: Optional[dict] = None,
        token_type: str = "bot",
    ) -> dict:
        """Call a Slack API method and verify ok=true.

        Returns the full response dict on success.
        Raises SlackApiError if ok is false.
        """
        resp = self._request(method_name, params=params, token_type=token_type)

        if not resp.get("ok"):
            raise SlackApiError(
                resp.get("error", "unknown_error"),
                body=resp,
            )

        return resp

    def paginate(
        self,
        method_name: str,
        params: Optional[dict] = None,
        token_type: str = "bot",
        limit: Optional[int] = None,
        response_key: Optional[str] = None,
    ) -> list:
        """Auto-paginate a Slack API method using cursor-based pagination.

        Args:
            method_name: Slack API method (e.g. "conversations.list")
            params: Initial parameters dict
            token_type: "bot", "user", or "auto"
            limit: Stop after collecting this many items total
            response_key: Key in response containing the list (e.g. "channels").
                          If None, attempts to auto-detect.

        Returns all items across pages.
        """
        all_items = []
        p = dict(params or {})
        # Use reasonable page size if not set
        if "limit" not in p:
            p["limit"] = 200

        while True:
            resp = self.call(method_name, params=p, token_type=token_type)

            # Find the list in the response
            items = []
            if response_key and response_key in resp:
                items = resp[response_key]
            else:
                # Auto-detect: find the first list value that isn't a string
                for key, val in resp.items():
                    if key in ("ok", "response_metadata", "cache_ts"):
                        continue
                    if isinstance(val, list):
                        items = val
                        break

            all_items.extend(items)

            if limit and len(all_items) >= limit:
                return all_items[:limit]

            # Check for next cursor
            metadata = resp.get("response_metadata", {})
            next_cursor = metadata.get("next_cursor", "")
            if not next_cursor:
                break
            p["cursor"] = next_cursor

        return all_items

    def upload_request(
        self,
        url: str,
        file_data: bytes,
        filename: str,
        token_type: str = "bot",
    ) -> None:
        """Upload file data to a pre-signed URL (step 2 of files.uploadV2).

        This uses a raw POST with the file bytes as body.
        """
        token = self._get_token(token_type)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        }

        req = urllib.request.Request(url, data=file_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, context=self._ctx, timeout=60) as resp:
                resp.read()  # Drain response
        except urllib.error.HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode("utf-8")
            except Exception:
                pass
            raise SlackApiError(
                f"File upload failed: {body_text}", status=e.code
            ) from e
        except urllib.error.URLError as e:
            print(f"Connection error during upload: {e.reason}", file=sys.stderr)
            sys.exit(1)
