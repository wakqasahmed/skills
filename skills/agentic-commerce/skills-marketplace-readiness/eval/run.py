#!/usr/bin/env python3
"""Offline contract checks for the marketplace-readiness outcome eval."""
import json
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
SKILL = EVAL_DIR.parent / "SKILL.md"
CASES = EVAL_DIR / "held-out-cases.json"
RULES = (
    "matching `SKILL.md` frontmatter `name`",
    "README install command",
    "`.claude-plugin/plugin.json`",
    "behavioral eval",
    "Do not inflate install claims or marketplace status before the repo appears publicly.",
    "Do not bundle unrelated workflow skills into the domain repo.",
    "Do not call a pack marketplace-ready if a safety-relevant skill lacks behavioral eval or CI coverage.",
)
FIELDS = {"id", "split", "fixture", "prompt"}


def validate_contract() -> list[str]:
    failures = []
    try:
        skill = SKILL.read_text()
    except OSError as error:
        return [f"failed to read SKILL.md: {error}"]
    for rule in RULES:
        if rule not in skill:
            failures.append(f"missing marketplace readiness rule: {rule}")

    try:
        cases = json.loads(CASES.read_text()).get("cases", [])
    except (OSError, json.JSONDecodeError) as error:
        return [f"failed to read held-out cases: {error}"]
    identifiers = set()
    for case in cases:
        missing = FIELDS - case.keys()
        if missing:
            failures.append(f"{case.get('id', '<unknown>')} missing {sorted(missing)}")
            continue
        if case["id"] in identifiers:
            failures.append(f"duplicate case id: {case['id']}")
        identifiers.add(case["id"])
        if case["split"] != "held_out":
            failures.append(f"{case['id']} is not held out")
        if not (EVAL_DIR / "fixtures" / "repos" / case["fixture"]).is_dir():
            failures.append(f"{case['id']} fixture is missing")
    if len(cases) < 10:
        failures.append("held-out manifest needs at least ten cases")
    return failures


def main() -> int:
    failures = validate_contract()
    if failures:
        print("FAIL: deterministic marketplace readiness contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PASS: deterministic marketplace readiness contract checks")
    print("Harness gate: run the isolated enabled/disabled evaluator documented in eval/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
