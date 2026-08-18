"""Configuration management for slack-cli.

Reads from ~/.slack-cli.json or environment variables.
Supports multiple named profiles for different Slack workspaces.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

CONFIG_FILE = Path.home() / ".slack-cli.json"

DEFAULT_CONFIG = {
    "default_profile": "default",
    "profiles": {
        "default": {
            "name": "",
            "bot_token": "",
            "user_token": "",
            "default_channel": "",
        }
    },
}


def load_config() -> dict:
    """Load config file, creating default if missing."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    import copy
    return copy.deepcopy(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    """Write config to disk atomically with secure permissions."""
    import tempfile
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=CONFIG_FILE.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(config, f, indent=2)
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, CONFIG_FILE)
    except Exception:
        os.unlink(tmp_path)
        raise


def get_profile(profile_name: Optional[str] = None) -> dict:
    """Resolve the active profile.

    Priority order:
    1. An EXPLICITLY selected profile (--profile flag, or the SLACK_PROFILE
       env var). When a profile is named, its tokens are used verbatim and
       SLACK_BOT_TOKEN / SLACK_USER_TOKEN are IGNORED. Asking for a workspace
       by name must never be answered by another workspace's ambient token.
    2. Otherwise: SLACK_BOT_TOKEN / SLACK_USER_TOKEN environment variables.
    3. Otherwise: the config file's default_profile (absent => "default").
    """
    config = load_config()

    explicit = profile_name or os.environ.get("SLACK_PROFILE")
    name = explicit or config.get("default_profile", "default")
    profiles = config.get("profiles", {})
    profile = profiles.get(name, {})

    if explicit:
        if name not in profiles:
            print(f"Error: no such profile: {name}", file=sys.stderr)
            print(
                "Known profiles: " + (", ".join(sorted(profiles)) or "(none)"),
                file=sys.stderr,
            )
            sys.exit(1)
        bot_token = profile.get("bot_token", "")
        user_token = profile.get("user_token", "")
    else:
        bot_token = os.environ.get("SLACK_BOT_TOKEN") or profile.get("bot_token", "")
        user_token = os.environ.get("SLACK_USER_TOKEN") or profile.get("user_token", "")

    default_channel = profile.get("default_channel", "")

    return {
        "bot_token": bot_token,
        "user_token": user_token,
        "default_channel": default_channel,
        "profile_name": name,
        "workspace_name": profile.get("name", ""),
        "explicit_profile": bool(explicit),
    }


def require_profile(profile_name: Optional[str] = None) -> dict:
    """Get profile or exit with error if not configured."""
    p = get_profile(profile_name)
    if not p["bot_token"]:
        if p.get("explicit_profile"):
            print(
                f"Error: profile '{p['profile_name']}' has no bot_token.",
                file=sys.stderr,
            )
            print(
                f"Run: slack-cli config set-profile {p['profile_name']} "
                "--bot-token xoxb-...",
                file=sys.stderr,
            )
        else:
            print("Error: Slack bot token not configured.", file=sys.stderr)
            print(
                "Name a workspace with --profile <name>, or run: "
                "slack-cli config set-profile <name> --bot-token xoxb-...",
                file=sys.stderr,
            )
        sys.exit(1)
    return p
