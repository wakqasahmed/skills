#!/usr/bin/env python3
"""Reconcile .claude-plugin/plugin.json's skill list with skills/*/*/SKILL.md on disk.

Keeps existing entries in their current order (dropping any that no longer
exist on disk), then appends newly-discovered skill folders, sorted, at the
end. Run after scripts/sync-from-source.sh copies updated skill folders in,
so new skills don't require a manual manifest edit.
"""
import json
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

if new_entries:
    print("Added to plugin.json:", ", ".join(new_entries))
removed = sorted(set(existing) - set(actual))
if removed:
    print("Removed from plugin.json (no longer on disk):", ", ".join(removed))
if not new_entries and not removed:
    print("plugin.json already in sync")
