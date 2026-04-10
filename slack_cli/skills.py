"""Skills management for slack-cli.

Discovers, installs, lists, and validates bundled SKILL.md files.
Modeled after n8n-cli's skills system.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Where bundled skills live inside the package
SKILLS_DATA_DIR = Path(__file__).parent / "skills_data"

# Where skills get installed for Claude Code
CLAUDE_SKILLS_DIR = Path.home() / ".claude" / "skills"

# Marker comment so we know which skills we installed
MARKER = "<!-- installed by slack-cli -->"


def _find_bundled_skills() -> list:
    """Find all SKILL.md files in the package's skills_data/ directory."""
    if not SKILLS_DATA_DIR.exists():
        return []
    return sorted(SKILLS_DATA_DIR.glob("*.md"))


def _parse_skill_frontmatter(path: Path) -> dict:
    """Parse YAML-ish frontmatter from a SKILL.md file.

    Returns dict with keys: name, description, command_name, tags, etc.
    """
    text = path.read_text()
    info = {"path": str(path), "filename": path.name}

    # Extract frontmatter block
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return info

    for line in match.group(1).splitlines():
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key == "tags":
                # Parse YAML list on one line: [a, b, c]
                val = [
                    t.strip().strip('"').strip("'")
                    for t in val.strip("[]").split(",")
                    if t.strip()
                ]
            info[key] = val

    return info


def _extract_cli_commands(path: Path) -> list:
    """Extract slack-cli commands referenced in a SKILL.md file."""
    text = path.read_text()
    # Match lines that look like CLI invocations
    pattern = r"slack-cli\s+([a-z][a-z0-9\-\s]+)"
    matches = re.findall(pattern, text)
    # Deduplicate and clean
    commands = []
    seen = set()
    for m in matches:
        cmd = m.strip().split("  ")[0]  # Stop at double-space
        cmd = re.sub(r"\s+", " ", cmd).strip()
        # Only keep the subcommand chain (e.g. "chat post", "methods search")
        parts = cmd.split()
        if len(parts) >= 1 and parts[0] not in seen:
            key = " ".join(parts[:2]) if len(parts) >= 2 else parts[0]
            if key not in seen:
                commands.append(key)
                seen.add(key)
    return commands


def install_skills(force: bool = False) -> None:
    """Install bundled SKILL.md files to ~/.claude/skills/."""
    skills = _find_bundled_skills()
    if not skills:
        print("No bundled skills found.", file=sys.stderr)
        sys.exit(1)

    CLAUDE_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    installed = 0
    skipped = 0

    for src in skills:
        dest = CLAUDE_SKILLS_DIR / src.name
        if dest.exists() and not force:
            # Check if it's one of ours
            existing = dest.read_text()
            if MARKER in existing:
                # Ours -- overwrite
                shutil.copy2(src, dest)
                installed += 1
            else:
                # Not ours -- skip
                print(f"  Skipped {src.name} (exists, not ours -- use --force)")
                skipped += 1
        else:
            shutil.copy2(src, dest)
            installed += 1

    print(f"Installed {installed} skill(s) to {CLAUDE_SKILLS_DIR}")
    if skipped:
        print(f"Skipped {skipped} (use --force to overwrite)")


def list_skills(as_json: bool = False) -> None:
    """List all bundled skills."""
    skills = _find_bundled_skills()
    if not skills:
        print("No bundled skills found.")
        return

    infos = [_parse_skill_frontmatter(s) for s in skills]

    if as_json:
        print(json.dumps(infos, indent=2))
        return

    print(f"{'Skill':<30} {'Command':<20} {'Description'}")
    print("-" * 90)
    for info in infos:
        name = info.get("name", info["filename"])
        cmd = info.get("command_name", "")
        desc = info.get("description", "")[:45]
        print(f"{name:<30} {cmd:<20} {desc}")
    print(f"\n{len(infos)} skill(s) bundled")


def doctor() -> None:
    """Validate skills: check CLI commands referenced in skills actually exist."""
    skills = _find_bundled_skills()
    if not skills:
        print("No bundled skills found.")
        return

    errors = 0
    warnings = 0
    checked = 0

    for skill_path in skills:
        info = _parse_skill_frontmatter(skill_path)
        name = info.get("name", skill_path.name)
        commands = _extract_cli_commands(skill_path)
        checked += 1

        for cmd in commands:
            # Validate by running slack-cli <cmd> --help
            parts = cmd.split()
            try:
                result = subprocess.run(
                    ["slack-cli"] + parts + ["--help"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    print(f"  ERROR: {name}: `slack-cli {cmd}` not found")
                    errors += 1
            except FileNotFoundError:
                print(f"  WARNING: slack-cli not on PATH, skipping validation")
                warnings += 1
                break
            except subprocess.TimeoutExpired:
                print(f"  WARNING: {name}: `slack-cli {cmd} --help` timed out")
                warnings += 1

        # Check if installed
        dest = CLAUDE_SKILLS_DIR / skill_path.name
        if not dest.exists():
            print(f"  WARNING: {name}: not installed (run: slack-cli skills install)")
            warnings += 1

    print(f"\nChecked {checked} skill(s): {errors} error(s), {warnings} warning(s)")
    if errors:
        sys.exit(1)
