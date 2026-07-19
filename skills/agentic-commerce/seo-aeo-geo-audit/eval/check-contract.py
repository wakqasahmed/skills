#!/usr/bin/env python3
"""Offline, deterministic contract checks; this does not score agent outcomes."""
import json
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
SKILL = EVAL_DIR.parent / "SKILL.md"
CASES = EVAL_DIR / "held-out-cases.json"
TARGET_AGENT = EVAL_DIR / "run_target_agent.py"
REQUIRED_SKILL_TEXT = (
    "cite the observed output for each finding",
    "Do not present an unverified crawl, schema, or content inference as an observed finding.",
    "do not make production changes during an audit.",
)


def validate_contract() -> list[str]:
    failures = []
    if not TARGET_AGENT.is_file():
        failures.append("missing repository target-agent runner")
    else:
        runner = TARGET_AGENT.read_text()
        if "expected" in runner:
            failures.append("target-agent runner must not receive outcome labels")
        if "workspace_request" not in runner or "run_target_agent" not in runner:
            failures.append("target-agent runner must pass workspace skill context to the target agent")
    skill = SKILL.read_text()
    for text in REQUIRED_SKILL_TEXT:
        if text not in skill:
            failures.append(f"missing non-negotiable audit rule: {text}")
    cases = json.loads(CASES.read_text()).get("cases", [])
    ids, counts = set(), {"use": 0, "do_not_use": 0}
    for case in cases:
        required = {"id", "split", "prompt", "expected_skill_usage", "input", "expected"}
        missing = required - case.keys()
        if missing:
            failures.append(f"{case.get('id', '<unknown>')} missing {sorted(missing)}")
            continue
        if case["id"] in ids:
            failures.append(f"duplicate case id: {case['id']}")
        ids.add(case["id"])
        if case["split"] != "held_out":
            failures.append(f"{case['id']} is not held out")
        if case["expected_skill_usage"] not in counts:
            failures.append(f"{case['id']} has invalid usage")
        else:
            counts[case["expected_skill_usage"]] += 1
        expected = case["expected"]
        if not isinstance(expected, dict) or not {"disposition", "finding_ids", "recommendation_ids", "evidence_sources"} <= expected.keys():
            failures.append(f"{case['id']} lacks an artifact outcome contract")
    if len(cases) < 10 or any(value < 5 for value in counts.values()):
        failures.append("held-out manifest needs at least five use and five do-not-use cases")
    return failures


def main() -> int:
    failures = validate_contract()
    if failures:
        print("FAIL: deterministic SEO/AEO/GEO contract checks")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PASS: deterministic SEO/AEO/GEO contract checks")
    print("Harness gate: run the isolated enabled/disabled artifact evaluator in eval/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
