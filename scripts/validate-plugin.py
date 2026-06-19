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
required_readme_text = [
    "npx skills@latest add wakqasahmed/skills",
    "npx skills@latest add wakqasahmed/ai-visibility-skills",
    "npx skills@latest add wakqasahmed/agentic-commerce-skills",
    "npx skills@latest add wakqasahmed/ai-engineering-workflow-skills",
]
missing_readme_text = [text for text in required_readme_text if text not in readme]
if missing_readme_text:
    raise SystemExit("Missing README install paths: " + ", ".join(missing_readme_text))

print(f"validated {len(skills)} plugin skills")
