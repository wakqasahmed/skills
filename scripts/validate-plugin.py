#!/usr/bin/env python3
import json
import re
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

missing_check_commands = []
for skill_path in (root / "skills").glob("*/*/SKILL.md"):
    if "references/checks.md" not in skill_path.read_text():
        continue
    checks_path = skill_path.parent / "references" / "checks.md"
    if not checks_path.is_file():
        missing_check_commands.append(str(checks_path.relative_to(root)))

if missing_check_commands:
    raise SystemExit("Skills reference missing check commands: " + ", ".join(missing_check_commands))

readme = (root / "README.md").read_text()
canonical_install = "npx skills@latest add wakqasahmed/skills"
if readme.count(canonical_install) != 1:
    raise SystemExit("README must contain exactly one canonical install path")

taxonomy = {
    "Agentic Commerce": {"agentic-commerce"},
    "AI Visibility": {"ai-visibility"},
    "Email Marketing": {"email-marketing"},
    "Engineering Workflow": {"engineering"},
    "PHP/Laravel/Filament": {"php", "laravel", "filament"},
    "Productivity/Product": {"productivity", "product"},
}
folder_categories = {
    folder: category for category, folders in taxonomy.items() for folder in folders
}

browse_skills = re.search(r"^## Browse Skills\s*$([\s\S]*?)(?=^## |\Z)", readme, re.MULTILINE)
if not browse_skills:
    raise SystemExit("README must contain a Browse Skills section")

category_links = []
navigated_skills = []
misfiled_skills = []
current_category = None
for line in browse_skills.group(1).splitlines():
    category_match = re.fullmatch(r"### (.+)", line)
    if category_match:
        current_category = category_match.group(1)
        category_links.append(current_category)
        continue

    skill_match = re.fullmatch(r"- \[[^]]+\]\(skills/([^/]+)/([^/]+)/\)", line)
    if skill_match:
        folder, skill = skill_match.groups()
        skill_path = f"skills/{folder}/{skill}"
        navigated_skills.append(skill_path)
        if folder_categories.get(folder) != current_category:
            misfiled_skills.append(skill_path)

unknown_folders = sorted(
    {Path(skill).parts[1] for skill in listed} - folder_categories.keys()
)
expected_categories = sorted(
    {
        folder_categories[Path(skill).parts[1]]
        for skill in listed
        if Path(skill).parts[1] in folder_categories
    }
)
navigation_errors = []
if sorted(category_links) != expected_categories or len(category_links) != len(set(category_links)):
    navigation_errors.append("category headings must list each taxonomy category exactly once")
if sorted(navigated_skills) != listed or len(navigated_skills) != len(set(navigated_skills)):
    navigation_errors.append("skill links must list each manifest skill exactly once")
if misfiled_skills:
    navigation_errors.append("skill links must appear under their taxonomy category")
if unknown_folders:
    navigation_errors.append("skill folders must belong to a taxonomy category")
if navigation_errors:
    raise SystemExit("README skill navigation: " + "; ".join(navigation_errors))

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
