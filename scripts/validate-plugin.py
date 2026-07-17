#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
validator_path = Path(__file__).relative_to(root)
plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
skills = plugin.get("skills", [])
missing = [skill for skill in skills if not (root / skill / "SKILL.md").is_file()]
if missing:
    raise SystemExit("Missing plugin skill paths: " + ", ".join(missing))

listed = sorted(skill.removeprefix("./") for skill in skills)
actual = sorted(str(path.parent.relative_to(root)) for path in (root / "skills").glob("*/*/SKILL.md"))
if listed != actual:
    extra = sorted(set(actual) - set(listed))
    stale = sorted(set(listed) - set(actual))
    details = []
    if extra:
        details.append("Unlisted skill folders: " + ", ".join(extra))
    if stale:
        details.append("Stale manifest entries: " + ", ".join(stale))
    raise SystemExit("; ".join(details))

readme = (root / "README.md").read_text()
canonical_install = "npx skills@latest add wakqasahmed/skills"
if readme.count(canonical_install) != 1:
    raise SystemExit("README must contain exactly one canonical install path")

former_source_repos = (
    "wakqasahmed/ai-visibility-skills",
    "wakqasahmed/agentic-commerce-skills",
    "wakqasahmed/ai-engineering-workflow-skills",
    "wakqasahmed/php-laravel-filament-skills",
    "wakqasahmed/email-marketing-skills",
)


def tracked_text_files():
    tracked_paths = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=root, text=True
    ).split("\0")
    for tracked_path in tracked_paths:
        if not tracked_path:
            continue
        path = root / tracked_path
        if not path.is_file():
            continue
        content = path.read_bytes()
        if b"\0" in content:
            continue
        try:
            yield Path(tracked_path), content.decode()
        except UnicodeDecodeError:
            continue


def is_forbidden_list_entry(path, line):
    return path == validator_path and line.strip().rstrip(",") in {
        f'"{repo}"' for repo in former_source_repos
    }


source_references = []
stale_automation = []
for path, content in tracked_text_files():
    for repo in former_source_repos:
        if any(repo in line and not is_forbidden_list_entry(path, line) for line in content.splitlines()):
            source_references.append(f"{path}: {repo}")
    if (
        "sync" in path.name.lower()
        and (path.parts[0] == "scripts" or path.parts[:2] == (".github", "workflows"))
    ):
        stale_automation.append(str(path))

if source_references:
    raise SystemExit("Tracked content refers to former source repos: " + ", ".join(source_references))
if stale_automation:
    raise SystemExit("Obsolete source-sync automation remains: " + ", ".join(stale_automation))

print(f"validated {len(skills)} plugin skills")
