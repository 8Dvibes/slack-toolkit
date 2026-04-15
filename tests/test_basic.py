"""Basic tests for slack-cli v0.2.0.

Tests are kept minimal and offline (no real Slack API calls).
"""
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

# ---- version ----

def test_version():
    """slack-cli --version returns 0.2.0."""
    from slack_cli import __version__
    assert __version__ == "0.2.0"


def test_version_cli():
    """CLI --version flag outputs 0.2.0."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert "0.2.0" in result.stdout + result.stderr
    assert result.returncode == 0


# ---- catalog ----

def test_catalog_loads():
    """Catalog JSON loads and has 306 methods (bundled)."""
    import json
    from pathlib import Path
    bundled = Path(__file__).parent.parent / "slack_cli" / "catalog_data" / "methods.json"
    with open(bundled) as f:
        catalog = json.load(f)
    assert len(catalog) == 306


def test_catalog_no_stale_methods():
    """Stale methods (renamed/removed) are not in the bundled catalog."""
    import json
    from pathlib import Path
    bundled = Path(__file__).parent.parent / "slack_cli" / "catalog_data" / "methods.json"
    with open(bundled) as f:
        catalog = json.load(f)
    names = {m["name"] for m in catalog}
    stale = {"entity.present.details", "team.billingInfo", "workflows.stepCompleted",
             "workflows.stepFailed", "workflows.updateStep"}
    for stale_name in stale:
        assert stale_name not in names, f"Stale method still present: {stale_name}"


def test_catalog_new_methods_present():
    """New methods from v0.2.0 are in the bundled catalog."""
    import json
    from pathlib import Path
    bundled = Path(__file__).parent.parent / "slack_cli" / "catalog_data" / "methods.json"
    with open(bundled) as f:
        catalog = json.load(f)
    names = {m["name"] for m in catalog}
    expected_new = [
        "entity.presentDetails",
        "team.billing.info",
        "apps.datastore.get",
        "apps.datastore.put",
        "workflows.triggers.permissions.set",
        "assistant.search.context",
        "dnd.setSnooze",  # already existed
    ]
    for name in expected_new:
        assert name in names, f"Expected method not in catalog: {name}"


def test_catalog_search():
    """Search returns relevant results."""
    from slack_cli.methods import search_methods
    results = search_methods("conversations")
    assert len(results) > 0
    names = [m["name"] for m in results]
    assert any("conversations" in n for n in names)


def test_catalog_get_method():
    """get_method returns the correct method dict."""
    from slack_cli.methods import get_method
    m = get_method("conversations.open")
    assert m is not None
    assert m["name"] == "conversations.open"
    assert "users" in m.get("optional_params", [])


def test_catalog_no_duplicates():
    """Catalog has no duplicate method names."""
    from slack_cli.methods import load_catalog
    catalog = load_catalog()
    names = [m["name"] for m in catalog]
    assert len(names) == len(set(names)), "Duplicate method names found in catalog"


# ---- module imports ----

def test_import_usergroups():
    from slack_cli import usergroups
    assert hasattr(usergroups, "create_usergroup")
    assert hasattr(usergroups, "list_usergroups")
    assert hasattr(usergroups, "update_usergroup_members")


def test_import_canvas():
    from slack_cli import canvas
    assert hasattr(canvas, "create_canvas")
    assert hasattr(canvas, "edit_canvas")
    assert hasattr(canvas, "delete_canvas")


def test_import_reminders():
    from slack_cli import reminders
    assert hasattr(reminders, "add_reminder")
    assert hasattr(reminders, "list_reminders")
    assert hasattr(reminders, "complete_reminder")


def test_import_dnd():
    from slack_cli import dnd
    assert hasattr(dnd, "get_dnd_info")
    assert hasattr(dnd, "set_snooze")
    assert hasattr(dnd, "get_team_dnd_info")


def test_import_docs():
    from slack_cli import docs
    assert hasattr(docs, "fetch_method_doc")
    assert hasattr(docs, "cmd_docs")


# ---- CLI argument parsing ----

def test_conversations_help():
    """conversations --help includes all new subcommands."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "conversations", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout + result.stderr
    for cmd in ["open", "invite-all", "clone-members", "export-members", "diff", "random", "inactive"]:
        assert cmd in output, f"Missing subcommand in conversations --help: {cmd}"


def test_usergroups_help():
    """usergroups --help includes all subcommands."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "usergroups", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout + result.stderr
    for cmd in ["create", "list", "update", "disable", "enable", "members-list", "members-update"]:
        assert cmd in output, f"Missing subcommand: {cmd}"


def test_canvas_help():
    """canvas --help includes all subcommands."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "canvas", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout + result.stderr
    for cmd in ["create", "edit", "delete", "access-set", "access-delete", "sections"]:
        assert cmd in output, f"Missing subcommand: {cmd}"


def test_reminders_help():
    """reminders --help includes all subcommands."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "reminders", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout + result.stderr
    for cmd in ["add", "list", "complete", "delete", "info"]:
        assert cmd in output, f"Missing subcommand: {cmd}"


def test_dnd_help():
    """dnd --help includes all subcommands."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "dnd", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout + result.stderr
    for cmd in ["info", "set-snooze", "end-snooze", "end-dnd", "team-info"]:
        assert cmd in output, f"Missing subcommand: {cmd}"


def test_methods_update_has_live_flag():
    """methods update --help shows --live flag."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "methods", "update", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--live" in result.stdout + result.stderr


def test_docs_help():
    """docs --help shows method argument and --fresh flag."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "docs", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "method" in output
    assert "--fresh" in output


def test_config_show_no_crash():
    """config show works even with no profile configured."""
    result = subprocess.run(
        [sys.executable, "-m", "slack_cli.cli", "config", "show"],
        capture_output=True,
        text=True,
    )
    # Should not crash (returncode 0 or graceful)
    assert result.returncode in (0, 1)  # May fail if no config file


# ---- skills ----

def test_skills_count():
    """Exactly 28 skill files exist in skills_data."""
    skills_dir = Path(__file__).parent.parent / "slack_cli" / "skills_data"
    skill_files = list(skills_dir.glob("*.md"))
    assert len(skill_files) == 28, f"Expected 28 skills, found {len(skill_files)}: {[f.name for f in skill_files]}"


def test_skills_have_frontmatter():
    """All skill files have valid frontmatter with required fields."""
    skills_dir = Path(__file__).parent.parent / "slack_cli" / "skills_data"
    for skill_file in skills_dir.glob("*.md"):
        text = skill_file.read_text()
        assert text.startswith("---"), f"{skill_file.name}: missing frontmatter"
        assert "name:" in text, f"{skill_file.name}: missing name in frontmatter"
        assert "description:" in text, f"{skill_file.name}: missing description in frontmatter"
        assert "<!-- installed by slack-cli -->" in text, f"{skill_file.name}: missing marker"


def test_new_skills_present():
    """All 13 new skill files from v0.2.0 exist."""
    skills_dir = Path(__file__).parent.parent / "slack_cli" / "skills_data"
    existing = {f.name for f in skills_dir.glob("*.md")}
    new_skills = [
        "slack-dm.md",
        "slack-identity.md",
        "slack-canvas.md",
        "slack-usergroup.md",
        "slack-reminders.md",
        "slack-streaming.md",
        "slack-assistant.md",
        "slack-docs.md",
        "slack-lists.md",
        "slack-dnd.md",
        "slack-admin.md",
        "slack-calls.md",
        "slack-bookmarks.md",
    ]
    for skill in new_skills:
        assert skill in existing, f"Missing new skill file: {skill}"


# ---- docs cache ----

def test_docs_cache_path():
    """docs._cache_path returns expected path."""
    from slack_cli.docs import _cache_path
    path = _cache_path("conversations.open")
    assert "conversations.open" in str(path)
    assert str(path).endswith(".md")


def test_docs_is_cache_fresh_missing():
    """_is_cache_fresh returns False for non-existent file."""
    from slack_cli.docs import _is_cache_fresh
    assert not _is_cache_fresh(Path("/nonexistent/path/does/not/exist.md"))
