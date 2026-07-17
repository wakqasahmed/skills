#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
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

former_source_repos = [
    "wakqasahmed/ai-visibility-skills",
    "wakqasahmed/agentic-commerce-skills",
    "wakqasahmed/ai-engineering-workflow-skills",
    "wakqasahmed/php-laravel-filament-skills",
    "wakqasahmed/email-marketing-skills",
]
source_references = [repo for repo in former_source_repos if repo in readme]
if source_references:
    raise SystemExit("README refers to former source repos: " + ", ".join(source_references))

obsolete_automation = [
    root / "scripts" / "sync-from-source.sh",
    root / "scripts" / "sync-plugin-manifest.py",
    root / ".github" / "workflows" / "sync-check.yml",
]
remaining_automation = [str(path.relative_to(root)) for path in obsolete_automation if path.exists()]
if remaining_automation:
    raise SystemExit("Obsolete source-sync automation remains: " + ", ".join(remaining_automation))

print(f"validated {len(skills)} plugin skills")
