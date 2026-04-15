"""Canvas operations for slack-cli."""

import json
import sys
from typing import Optional

from .client import SlackClient


def create_canvas(
    client: SlackClient,
    title: Optional[str] = None,
    content: Optional[str] = None,
    channel_id: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Create a new canvas."""
    params = {}
    if title:
        params["title"] = title
    if content:
        # Wrap markdown content in document_content format
        params["document_content"] = {
            "type": "markdown",
            "markdown": content,
        }
    if channel_id:
        # Use conversations.canvases.create if channel_id provided
        params["channel_id"] = channel_id

    method = "conversations.canvases.create" if channel_id else "canvases.create"
    resp = client.call(method, params=params)
    canvas = resp.get("canvas", {})

    if as_json:
        print(json.dumps(canvas if canvas else resp, indent=2))
        return

    canvas_id = canvas.get("canvas_id", resp.get("canvas_id", ""))
    print(f"Created canvas: {canvas_id}")
    if title:
        print(f"  Title: {title}")


def edit_canvas(
    client: SlackClient,
    canvas_id: str,
    changes: str,
    as_json: bool = False,
) -> None:
    """Edit a canvas using change operations (JSON array).

    changes: JSON array of change operations e.g.:
    '[{"operation":"insert_at_end","document_content":{"type":"markdown","markdown":"New content"}}]'
    """
    try:
        changes_list = json.loads(changes)
    except json.JSONDecodeError as e:
        print(f"Error: --changes must be a valid JSON array: {e}", file=sys.stderr)
        sys.exit(1)

    params = {"canvas_id": canvas_id, "changes": changes_list}
    resp = client.call("canvases.edit", params=params)

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Canvas {canvas_id} updated.")


def delete_canvas(
    client: SlackClient,
    canvas_id: str,
    as_json: bool = False,
) -> None:
    """Delete a canvas."""
    resp = client.call("canvases.delete", params={"canvas_id": canvas_id})

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Deleted canvas: {canvas_id}")


def set_canvas_access(
    client: SlackClient,
    canvas_id: str,
    access_level: str,
    user_ids: Optional[str] = None,
    channel_ids: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Set access for a canvas."""
    params = {"canvas_id": canvas_id, "access_level": access_level}
    if user_ids:
        params["user_ids"] = user_ids.split(",")
    if channel_ids:
        params["channel_ids"] = channel_ids.split(",")

    resp = client.call("canvases.access.set", params=params)

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Canvas {canvas_id} access set to: {access_level}")


def delete_canvas_access(
    client: SlackClient,
    canvas_id: str,
    user_ids: Optional[str] = None,
    channel_ids: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Delete (revoke) access for a canvas."""
    params = {"canvas_id": canvas_id}
    if user_ids:
        params["user_ids"] = user_ids.split(",")
    if channel_ids:
        params["channel_ids"] = channel_ids.split(",")

    resp = client.call("canvases.access.delete", params=params)

    if as_json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Access revoked on canvas: {canvas_id}")


def list_canvas_sections(
    client: SlackClient,
    canvas_id: str,
    contains_text: Optional[str] = None,
    as_json: bool = False,
) -> None:
    """Look up sections in a canvas."""
    params = {"canvas_id": canvas_id}
    if contains_text:
        params["criteria"] = {"contains_text": contains_text}

    resp = client.call("canvases.sections.lookup", params=params)
    sections = resp.get("sections", [])

    if as_json:
        print(json.dumps(sections, indent=2))
        return

    if not sections:
        print("No sections found.")
        return

    for i, section in enumerate(sections, 1):
        sid = section.get("id", "")
        stype = section.get("type", "")
        print(f"  [{i}] {sid} (type: {stype})")
    print(f"\nTotal: {len(sections)} section(s)")
