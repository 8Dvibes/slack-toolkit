"""File operations for slack-cli.

Uses the NEW two-step upload flow (files.getUploadURLExternal + files.completeUploadExternal).
The old files.upload endpoint is retired.
"""

import json
import os
import sys
from typing import Optional

from .client import SlackClient


def upload_file(
    client: SlackClient,
    filepath: str,
    channels: Optional[str] = None,
    title: Optional[str] = None,
    initial_comment: Optional[str] = None,
    thread_ts: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Upload a file using the two-step V2 flow.

    Step 1: files.getUploadURLExternal - get a pre-signed upload URL
    Step 2: POST file data to the upload URL
    Step 3: files.completeUploadExternal - finalize and share
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)

    if title is None:
        title = filename

    # Step 1: Get upload URL
    step1_params = {
        "filename": filename,
        "length": file_size,
    }
    resp1 = client.call("files.getUploadURLExternal", params=step1_params)
    upload_url = resp1.get("upload_url", "")
    file_id = resp1.get("file_id", "")

    if not upload_url:
        print("Error: No upload URL returned.", file=sys.stderr)
        sys.exit(1)

    # Step 2: Upload file data to the pre-signed URL
    with open(filepath, "rb") as f:
        file_data = f.read()

    client.upload_request(upload_url, file_data, filename)

    # Step 3: Complete the upload
    step3_params = {
        "files": [{"id": file_id, "title": title}],
    }
    if channels:
        step3_params["channel_id"] = channels.split(",")[0]  # Primary channel
    if initial_comment:
        step3_params["initial_comment"] = initial_comment
    if thread_ts:
        step3_params["thread_ts"] = thread_ts

    resp3 = client.call("files.completeUploadExternal", params=step3_params)

    if as_json:
        print(json.dumps(resp3, indent=2))
        return

    files = resp3.get("files", [])
    if files:
        f = files[0]
        print(f"Uploaded: {f.get('id', file_id)} - {f.get('title', title)}")
    else:
        print(f"Uploaded: {file_id} - {title}")


def list_files(
    client: SlackClient,
    channel: Optional[str] = None,
    user: Optional[str] = None,
    types: Optional[str] = None,
    count: int = 100,
    as_json: bool = False,
) -> None:
    """List files."""
    params = {"count": count}
    if channel:
        params["channel"] = channel
    if user:
        params["user"] = user
    if types:
        params["types"] = types

    resp = client.call("files.list", params=params)
    files = resp.get("files", [])

    if as_json:
        print(json.dumps(files, indent=2))
        return

    if not files:
        print("No files found.")
        return

    print(f"{'ID':<15} {'Type':<10} {'Size':<10} {'Name'}")
    print("-" * 70)
    for f in files:
        fid = f.get("id", "")
        ftype = f.get("filetype", "")
        size = f.get("size", 0)
        name = f.get("name", "untitled")
        # Human-readable size
        if size >= 1_048_576:
            size_str = f"{size / 1_048_576:.1f}MB"
        elif size >= 1024:
            size_str = f"{size / 1024:.1f}KB"
        else:
            size_str = f"{size}B"
        print(f"{fid:<15} {ftype:<10} {size_str:<10} {name}")
    print(f"\nTotal: {len(files)} file(s)")


def get_file_info(
    client: SlackClient,
    file_id: str,
    as_json: bool = False,
) -> None:
    """Get info about a file."""
    resp = client.call("files.info", params={"file": file_id})
    f = resp.get("file", {})

    if as_json:
        print(json.dumps(f, indent=2))
        return

    print(f"ID:        {f.get('id', '')}")
    print(f"Name:      {f.get('name', '')}")
    print(f"Title:     {f.get('title', '')}")
    print(f"Type:      {f.get('filetype', '')}")
    print(f"Size:      {f.get('size', 0)} bytes")
    print(f"User:      {f.get('user', '')}")
    print(f"Created:   {f.get('created', '')}")
    print(f"URL:       {f.get('url_private', '')}")
    channels = f.get("channels", [])
    if channels:
        print(f"Channels:  {', '.join(channels)}")


def delete_file(
    client: SlackClient,
    file_id: str,
    as_json: bool = False,
) -> None:
    """Delete a file."""
    resp = client.call("files.delete", params={"file": file_id})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Deleted file: {file_id}")
