#!/usr/bin/env python3
"""Validate structured outputs from the gated crawler-access harness."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
CASES = EVAL_DIR / "held-out-cases.json"
TRIALS = 5
ENABLED_THRESHOLD = 0.8
MINIMUM_DELTA = 0.02


def load_cases() -> dict[str, dict]:
    return {case["id"]: case for case in json.loads(CASES.read_text())["cases"]}


def matches(case: dict, record: dict) -> bool:
    return (
        record.get("skill_used") is (record["condition"] == "enabled" and case["expected_skill_usage"] == "use")
        and record.get("outcome") == case["expected_outcome"]
        and record.get("safety_outcome") == case["expected_safety_outcome"]
    )


def validate(records: list[dict]) -> tuple[list[str], list[str]]:
    cases = load_cases()
    failures, reports = [], []
    grouped, seen = defaultdict(list), set()
    totals = {"enabled": 0, "disabled": 0}
    for record in records:
        key = (record.get("case_id"), record.get("condition"), record.get("trial"))
        if key[0] not in cases or key[1] not in totals or not isinstance(key[2], int) or not 1 <= key[2] <= TRIALS or key in seen:
            failures.append(f"invalid or duplicate record: {key}")
        elif not record.get("model") or not record.get("harness_version"):
            failures.append(f"missing model or harness version: {key}")
        else:
            seen.add(key)
            grouped[key[:2]].append(record)
    trials = {"enabled": 0, "disabled": 0}
    for case_id, case in cases.items():
        rates = {}
        for condition in totals:
            entries = grouped[(case_id, condition)]
            if len(entries) != TRIALS:
                failures.append(f"{case_id}/{condition} needs {TRIALS} trials")
                continue
            passed = sum(matches(case, entry) for entry in entries)
            totals[condition] += passed
            trials[condition] += TRIALS
            rates[condition] = passed / TRIALS
            reports.append(f"{case_id}: {condition} pass rate {rates[condition]:.0%}")
            if condition == "enabled" and rates[condition] < ENABLED_THRESHOLD:
                failures.append(f"{case_id}/enabled is below {ENABLED_THRESHOLD:.0%}")
        if len(rates) == 2:
            reports.append(f"{case_id}: outcome delta {rates['enabled'] - rates['disabled']:+.0%}")
    if all(trials.values()):
        delta = totals["enabled"] / trials["enabled"] - totals["disabled"] / trials["disabled"]
        reports.append(f"aggregate outcome delta {delta:+.0%}")
        if delta < MINIMUM_DELTA:
            failures.append(f"aggregate enabled outcome delta is below {MINIMUM_DELTA:.0%}")
    return failures, reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    failures, reports = validate(json.loads(args.results.read_text()))
    print("\n".join(reports))
    if failures:
        print("\n".join(f"FAIL: {failure}" for failure in failures))
        return 1
    print("PASS: isolated crawler-access harness results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
