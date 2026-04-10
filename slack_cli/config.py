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
    """Resolve the active profile, with env-var overrides.

    Priority order:
    1. Environment variables (SLACK_BOT_TOKEN, SLACK_USER_TOKEN)
    2. Named profile from config file
    3. default profile from config file
    """
    config = load_config()

    name = (
        profile_name
        or os.environ.get("SLACK_PROFILE")
        or config.get("default_profile", "default")
    )
    profiles = config.get("profiles", {})
    profile = profiles.get(name, {})

    bot_token = os.environ.get("SLACK_BOT_TOKEN") or profile.get("bot_token", "")
    user_token = os.environ.get("SLACK_USER_TOKEN") or profile.get("user_token", "")
    default_channel = profile.get("default_channel", "")

    return {
        "bot_token": bot_token,
        "user_token": user_token,
        "default_channel": default_channel,
        "profile_name": name,
        "workspace_name": profile.get("name", ""),
    }


def require_profile(profile_name: Optional[str] = None) -> dict:
    """Get profile or exit with error if not configured."""
    p = get_profile(profile_name)
    if not p["bot_token"]:
        print("Error: Slack bot token not configured.", file=sys.stderr)
        print(
            "Set SLACK_BOT_TOKEN env var or run: slack-cli config set-profile <name> --bot-token xoxb-...",
            file=sys.stderr,
        )
        sys.exit(1)
    return p
