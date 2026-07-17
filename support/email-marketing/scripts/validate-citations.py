#!/usr/bin/env python3
import datetime
import json
import re
import sys
from pathlib import Path

support_root = Path(__file__).resolve().parents[1]
root = support_root.parents[1]
errors = []
warnings = []

index = json.loads((support_root / "SOURCE_INDEX.json").read_text())
table_ids = set(re.findall(r"^\| `([A-Z0-9-]+)` \|", (support_root / "SOURCES.md").read_text(), re.M))

if set(index) != table_ids:
    errors.append(
        f"SOURCE_INDEX.json and SOURCES.md disagree: only in index {sorted(set(index) - table_ids)}, "
        f"only in table {sorted(table_ids - set(index))}"
    )

manifest = json.loads((support_root / "manifest.json").read_text())
if manifest.get("source_count") != len(index):
    errors.append(f"manifest.json source_count is {manifest.get('source_count')}, registry has {len(index)}")

skill_files = sorted((root / "skills" / "email-marketing").glob("*/SKILL.md"))
if manifest.get("skill_count") != len(skill_files):
    errors.append(f"manifest.json skill_count is {manifest.get('skill_count')}, repo has {len(skill_files)}")

used = set()
for path in [support_root / "GLOBAL_GUARDRAILS.md", *skill_files]:
    unregistered = set()
    for cite in re.findall(r"\[([A-Z][A-Z0-9-]*-\d+)\]", path.read_text()):
        used.add(cite)
        if cite not in index:
            unregistered.add(cite)
    for cite in sorted(unregistered):
        errors.append(f"{path.relative_to(root)} cites unregistered ID [{cite}]")

unused = sorted(set(index) - used)
if unused:
    errors.append(f"registered but never cited: {unused}")

today = datetime.date.today()
for path in [support_root / "SOURCES.md", support_root / "GLOBAL_GUARDRAILS.md", *skill_files]:
    match = re.search(r"^(?:last_reviewed|Last reviewed): (\d{4}-\d{2}-\d{2})$", path.read_text(), re.M)
    if not match:
        errors.append(f"{path.relative_to(root)} has no last_reviewed date")
        continue
    age = (today - datetime.date.fromisoformat(match.group(1))).days
    if age > 180:
        warnings.append(f"{path.relative_to(root)} last reviewed {age} days ago; re-verify its sources")

import os
for warning in warnings:
    prefix = "::warning::" if os.environ.get("GITHUB_ACTIONS") else "WARNING: "
    print(f"{prefix}{warning}")
if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    sys.exit(1)
print(f"citations OK: {len(used)} IDs cited, {len(index)} registered, registries consistent")
