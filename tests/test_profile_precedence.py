"""Profile-vs-environment precedence (v0.4.0).

Regression tests for the workspace collision fixed in 0.4.0: an ambient
SLACK_BOT_TOKEN used to override an explicitly named --profile, so asking for
workspace B was answered with workspace A's token. Offline; no Slack calls.

Fixture values are deliberately NOT in Slack's real token format -- nothing here
should ever resemble a credential.
"""
import pytest

from slack_cli import config as cfg

BOT_A = "FAKE-BOT-WORKSPACE-A-AMBIENT"
BOT_B = "FAKE-BOT-WORKSPACE-B-PROFILE"
USER_A = "FAKE-USER-WORKSPACE-A"
USER_B = "FAKE-USER-WORKSPACE-B"

CONFIG = {
    "profiles": {
        "a": {"name": "Workspace A", "bot_token": BOT_A, "user_token": USER_A},
        "b": {"name": "Workspace B", "bot_token": BOT_B, "user_token": USER_B},
        "default": {"name": "", "bot_token": "", "user_token": ""},
    },
    "default_profile": "a",
}


@pytest.fixture
def cfg_file(monkeypatch):
    monkeypatch.setattr(cfg, "load_config", lambda: {
        "profiles": {k: dict(v) for k, v in CONFIG["profiles"].items()},
        "default_profile": CONFIG["default_profile"],
    })
    for var in ("SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "SLACK_PROFILE"):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


def test_explicit_profile_beats_ambient_env(cfg_file):
    """--profile b must NOT be answered by an ambient workspace-A token."""
    cfg_file.setenv("SLACK_BOT_TOKEN", BOT_A)
    p = cfg.get_profile("b")
    assert p["bot_token"] == BOT_B
    assert p["profile_name"] == "b"
    assert p["workspace_name"] == "Workspace B"
    assert p["explicit_profile"] is True


def test_slack_profile_env_also_beats_ambient_token(cfg_file):
    """SLACK_PROFILE selected the name but not the token before 0.4.0."""
    cfg_file.setenv("SLACK_BOT_TOKEN", BOT_A)
    cfg_file.setenv("SLACK_PROFILE", "b")
    p = cfg.get_profile()
    assert p["bot_token"] == BOT_B
    assert p["profile_name"] == "b"


def test_explicit_profile_ignores_ambient_user_token(cfg_file):
    cfg_file.setenv("SLACK_USER_TOKEN", "FAKE-USER-AMBIENT")
    p = cfg.get_profile("b")
    assert p["user_token"] == USER_B


def test_env_still_used_when_no_profile_named(cfg_file):
    """CI/container setups that only export tokens keep working."""
    cfg_file.setenv("SLACK_BOT_TOKEN", "FAKE-BOT-FROM-CI")
    p = cfg.get_profile()
    assert p["bot_token"] == "FAKE-BOT-FROM-CI"
    assert p["explicit_profile"] is False


def test_default_profile_used_when_nothing_set(cfg_file):
    p = cfg.get_profile()
    assert p["bot_token"] == BOT_A
    assert p["profile_name"] == "a"


def test_unknown_explicit_profile_exits(cfg_file, capsys):
    """A typo must fail loudly, not fall through to the ambient token."""
    cfg_file.setenv("SLACK_BOT_TOKEN", BOT_A)
    with pytest.raises(SystemExit) as e:
        cfg.get_profile("ranchh")
    assert e.value.code == 1
    err = capsys.readouterr().err
    assert "no such profile: ranchh" in err
    assert "Known profiles:" in err


def test_named_profile_without_token_names_itself(cfg_file, capsys):
    with pytest.raises(SystemExit) as e:
        cfg.require_profile("default")
    assert e.value.code == 1
    assert "profile 'default' has no bot_token" in capsys.readouterr().err


def test_unnamed_call_with_no_token_tells_you_to_name_one(cfg_file, monkeypatch):
    monkeypatch.setattr(cfg, "load_config", lambda: {"profiles": {}})
    with pytest.raises(SystemExit):
        cfg.require_profile()
