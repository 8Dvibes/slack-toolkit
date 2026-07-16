from pathlib import Path

from slack_cli.skills import _extract_cli_commands


def _skill(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "SKILL.md"
    path.write_text(body)
    return path


def test_command_extraction_does_not_treat_prose_as_commands(tmp_path):
    path = _skill(
        tmp_path,
        """---
description: Learn slack-cli best practices.
tags: [slack-cli, agents]
---

Use slack-cli when the task needs Slack. The CLI does not guess.
""",
    )

    assert _extract_cli_commands(path) == []


def test_command_extraction_reads_shell_lines_and_inline_code(tmp_path):
    path = _skill(
        tmp_path,
        """Run `slack-cli api auth.test` first.

```bash
$ slack-cli conversations list --limit 10
slack-cli chat post C123 hello
```
""",
    )

    assert _extract_cli_commands(path) == [
        "conversations list",
        "chat post",
        "api auth.test",
    ]


def test_command_extraction_deduplicates_examples(tmp_path):
    path = _skill(
        tmp_path,
        """`slack-cli config show`

slack-cli config show
""",
    )

    assert _extract_cli_commands(path) == ["config show"]
