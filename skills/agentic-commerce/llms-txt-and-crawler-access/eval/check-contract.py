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
    try:
        skill = SKILL.read_text()
    except OSError as error:
        print("FAIL: llms/crawler static contract")
        print(f"cannot read SKILL.md: {error}")
        return 1

    failures = [f"missing SKILL.md contract: {term}" for term in REQUIRED_SKILL_TEXT if term not in skill]
    try:
        cases = json.loads(CASES.read_text()).get("cases")
    except OSError as error:
        print("FAIL: llms/crawler static contract")
        print(f"cannot read held-out cases: {error}")
        return 1
    except json.JSONDecodeError as error:
        print("FAIL: llms/crawler static contract")
        print(f"invalid held-out cases JSON: {error}")
        return 1
    if not isinstance(cases, list):
        print("FAIL: llms/crawler static contract")
        print("held-out cases must contain a cases list")
        return 1

    if len(cases) < 10:
        failures.append("fewer than 10 held-out cases")
    usage = {"use": 0, "do_not_use": 0}
    for case in cases:
        missing = REQUIRED_CASE_FIELDS - case.keys()
        if missing or case["split"] != "held_out" or not case["expected_safety_outcome"]:
            failures.append(f"invalid held-out case: {case.get('id', '<unknown>')}")
            continue
        skill_usage = case["expected_skill_usage"]
        if skill_usage not in usage:
            failures.append(f"invalid expected_skill_usage '{skill_usage}' in case: {case.get('id', '<unknown>')}")
            continue
        usage[skill_usage] += 1
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
