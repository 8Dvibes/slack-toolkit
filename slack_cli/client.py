"""HTTP client for the Slack Web API. Zero external dependencies (urllib only)."""

import http.client
import json
import os
import ssl
import sys
import tempfile
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
        body_format: str = "form",
    ) -> dict:
        """POST to https://slack.com/api/{method_name}.

        Defaults to application/x-www-form-urlencoded: every Web API method
        accepts it, while only a documented subset of write methods accepts
        application/json. GET-style methods (conversations.list, users.list,
        ...) silently IGNORE a JSON body -- params like `types` and `cursor`
        are dropped with no error. Dict/list values are JSON-serialized into
        their form field, which Slack accepts (e.g. blocks, attachments).

        Handles rate limiting with exponential backoff + jitter.
        Returns the parsed JSON response dict.
        """
        import random

        url = f"{self.BASE_URL}{method_name}"
        token = self._get_token(token_type)
        if body_format == "json":
            content_type = "application/json; charset=utf-8"
            data = json.dumps(params or {}).encode("utf-8")
        elif body_format == "form":
            content_type = "application/x-www-form-urlencoded"
            form_params = {}
            for key, value in (params or {}).items():
                if value is None:
                    continue
                if isinstance(value, (dict, list)):
                    form_params[key] = json.dumps(value, separators=(",", ":"))
                elif isinstance(value, bool):
                    form_params[key] = "true" if value else "false"
                else:
                    form_params[key] = value
            data = urllib.parse.urlencode(form_params).encode("utf-8")
        else:
            raise ValueError(f"Unsupported request body format: {body_format}")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        }

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
        body_format: str = "form",
    ) -> dict:
        """Call a Slack API method and verify ok=true.

        Form-encoded by default (see _request). Pass body_format="json" only
        for methods documented to accept JSON bodies.

        Returns the full response dict on success.
        Raises SlackApiError if ok is false.
        """
        resp = self._request(
            method_name,
            params=params,
            token_type=token_type,
            body_format=body_format,
        )

        if not resp.get("ok"):
            raise SlackApiError(
                resp.get("error", "unknown_error"),
                body=resp,
            )

        return resp

    def call_form(
        self,
        method_name: str,
        params: Optional[dict] = None,
        token_type: str = "bot",
    ) -> dict:
        """Call a Slack API method using application/x-www-form-urlencoded.

        Kept for back-compat; form encoding is now the default for call().
        """
        return self.call(
            method_name,
            params=params,
            token_type=token_type,
            body_format="form",
        )

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

        The upload URL is already authorized. Do not send Slack bearer auth here.
        """
        safe_filename = filename.replace("\\", "\\\\").replace('"', '\\"')
        boundary = f"----slack-cli-upload-{int(time.time() * 1000)}"
        body = b"".join(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                (
                    'Content-Disposition: form-data; name="filename"; '
                    f'filename="{safe_filename}"\r\n'
                ).encode("utf-8"),
                b"Content-Type: application/octet-stream\r\n\r\n",
                file_data,
                b"\r\n",
                f"--{boundary}--\r\n".encode("utf-8"),
            ]
        )
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        }

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

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

    def download_request(
        self,
        url: str,
        output_path: str,
        token_type: str = "bot",
        chunk_size: int = 1024 * 1024,
    ) -> int:
        """Download a private Slack file to disk with bearer authentication.

        Bytes are streamed in chunks to a temporary file beside the destination,
        then atomically moved into place after a successful download. This keeps
        memory usage bounded and avoids leaving a partial destination file.

        Returns the number of bytes written.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        token = self._get_token(token_type)
        headers = {"Authorization": f"Bearer {token}"}
        req = urllib.request.Request(url, headers=headers, method="GET")
        temp_path = None

        try:
            with urllib.request.urlopen(req, context=self._ctx, timeout=60) as resp:
                status = getattr(resp, "status", None)
                if status is None and hasattr(resp, "getcode"):
                    status = resp.getcode()
                if status is not None and not 200 <= status < 300:
                    raise SlackApiError(
                        f"File download failed: HTTP {status}", status=status
                    )

                output_path = os.fspath(output_path)
                output_dir = os.path.dirname(os.path.abspath(output_path))
                output_name = os.path.basename(output_path) or "slack-download"
                total_bytes = 0

                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    dir=output_dir,
                    prefix=f".{output_name}.",
                    suffix=".part",
                    delete=False,
                ) as output_file:
                    temp_path = output_file.name
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        output_file.write(chunk)
                        total_bytes += len(chunk)

                os.replace(temp_path, output_path)
                temp_path = None
                return total_bytes
        except SlackApiError:
            raise
        except urllib.error.HTTPError as e:
            raise SlackApiError(
                f"File download failed: HTTP {e.code} {e.reason}", status=e.code
            ) from e
        except urllib.error.URLError as e:
            raise SlackApiError(f"File download connection failed: {e.reason}") from e
        except (OSError, http.client.HTTPException) as e:
            raise SlackApiError(f"Could not save downloaded file: {e}") from e
        finally:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
