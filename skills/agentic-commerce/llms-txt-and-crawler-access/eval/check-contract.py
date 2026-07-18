#!/usr/bin/env python3
"""Offline static contract for public crawler access recommendations."""
import json
from pathlib import Path


EVAL_DIR = Path(__file__).parent
SKILL = EVAL_DIR.parent / "SKILL.md"
CASES = EVAL_DIR / "held-out-cases.json"
REQUIRED_SKILL_TEXT = (
    "robots.txt",
    "sitemap",
    "llms.txt",
    "canonical URLs",
    "Never recommend opening admin, cart, checkout session, account, or private order paths to crawlers.",
    "public storefront evidence",
)
REQUIRED_CASE_FIELDS = {"id", "split", "prompt", "expected_skill_usage", "expected_outcome", "expected_safety_outcome"}


def main() -> int:
    skill = SKILL.read_text()
    failures = [f"missing SKILL.md contract: {term}" for term in REQUIRED_SKILL_TEXT if term not in skill]
    cases = json.loads(CASES.read_text())["cases"]
    if len(cases) < 10:
        failures.append("fewer than 10 held-out cases")
    usage = {"use": 0, "do_not_use": 0}
    for case in cases:
        missing = REQUIRED_CASE_FIELDS - case.keys()
        if missing or case["split"] != "held_out" or not case["expected_safety_outcome"]:
            failures.append(f"invalid held-out case: {case.get('id', '<unknown>')}")
            continue
        if case["expected_skill_usage"] in usage:
            usage[case["expected_skill_usage"]] += 1
    if any(count < 5 for count in usage.values()):
        failures.append("held-out cases must include at least 5 use and 5 do-not-use cases")
    if failures:
        print("FAIL: llms/crawler static contract")
        print("\n".join(failures))
        return 1
    print("PASS: llms/crawler static contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
