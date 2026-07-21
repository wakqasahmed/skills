#!/usr/bin/env python3
"""Reconcile generated plugin and README skill navigation with skills on disk.

Keeps existing entries in their current order (dropping any that no longer
exist on disk), then appends newly-discovered skill folders, sorted, at the
end. Run after scripts/sync-from-source.sh copies updated skill folders in,
so new skills don't require a manual manifest edit.
"""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest_path = root / ".claude-plugin" / "plugin.json"
plugin = json.loads(manifest_path.read_text())

existing = plugin.get("skills", [])
actual = sorted(
    "./" + str(path.parent.relative_to(root))
    for path in (root / "skills").glob("*/*/SKILL.md")
)

kept = [entry for entry in existing if entry in actual]
new_entries = sorted(set(actual) - set(kept))

plugin["skills"] = kept + new_entries
manifest_path.write_text(json.dumps(plugin, indent=2) + "\n")

taxonomy = {
    "Agentic Commerce": {"agentic-commerce"},
    "AI Visibility": {"ai-visibility"},
    "Email Marketing": {"email-marketing"},
    "Engineering Workflow": {"engineering"},
    "PHP/Laravel/Filament": {"php", "laravel", "filament"},
    "Productivity/Product": {"productivity", "product"},
}
readme_path = root / "README.md"
readme = readme_path.read_text()
browse_skills = re.search(r"(^## Browse Skills\s*$)([\s\S]*?)(?=^## |\Z)", readme, re.MULTILINE)
if not browse_skills:
    raise SystemExit("README must contain a Browse Skills section")

existing_labels = {
    f"skills/{folder}/{skill}": label
    for label, folder, skill in re.findall(
        r"- \[([^]]+)\]\(skills/([^/]+)/([^/]+)/\)", browse_skills.group(2)
    )
}
prologue, _, _ = browse_skills.group(2).partition("### ")
navigation = []
for category, folders in taxonomy.items():
    category_skills = [
        skill.removeprefix("./")
        for skill in plugin["skills"]
        if Path(skill).parts[1] in folders
    ]
    if not category_skills:
        continue
    navigation.append(f"### {category}")
    for skill_path in category_skills:
        _, folder, skill = skill_path.split("/")
        label = existing_labels.get(skill_path, skill.replace("-", " ").title())
        navigation.append(f"- [{label}]({skill_path}/)")

readme_path.write_text(
    readme[: browse_skills.start(2)]
    + prologue
    + "\n".join(navigation)
    + "\n\n"
    + readme[browse_skills.end(2) :]
)

if new_entries:
    print("Added to plugin.json:", ", ".join(new_entries))
removed = sorted(set(existing) - set(actual))
if removed:
    print("Removed from plugin.json (no longer on disk):", ", ".join(removed))
if not new_entries and not removed:
    print("plugin.json already in sync")
