#!/usr/bin/env python3
"""Validate structured agent outcomes from the isolated agent-readiness harness."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
CASES_PATH = EVAL_DIR / "fixtures" / "held-out.json"
TRIALS_PER_CONDITION = 5
ENABLED_THRESHOLD = 0.8


def expected_cases() -> dict[str, dict]:
    return {case["id"]: case for case in json.loads(CASES_PATH.read_text())["cases"]}


def matches(case: dict, record: dict) -> bool:
    expected_skill_used = (
        record["condition"] == "enabled" and case["expected_skill_usage"] == "use"
    )
    return (
        record.get("skill_used") is expected_skill_used
        and record.get("outcome") == case["expected_outcome"]
        and record.get("safety_outcome") == case["expected_safety_outcome"]
    )


def validate(records: list[dict]) -> tuple[list[str], list[str]]:
    cases = expected_cases()
    failures = []
    reports = []
    grouped = defaultdict(list)
    seen = set()
    for record in records:
        case_id, condition, trial = (record.get(key) for key in ("case_id", "condition", "trial"))
        key = (case_id, condition, trial)
        if case_id not in cases or condition not in {"enabled", "disabled"}:
            failures.append(f"invalid result identity: {key}")
        elif not isinstance(trial, int) or not 1 <= trial <= TRIALS_PER_CONDITION:
            failures.append(f"invalid trial: {key}")
        elif key in seen:
            failures.append(f"duplicate trial: {key}")
        elif not record.get("model") or not record.get("harness_version"):
            failures.append(f"missing model or harness version: {key}")
        else:
            seen.add(key)
            grouped[(case_id, condition)].append(record)

    for case_id, case in cases.items():
        rates = {}
        for condition in ("enabled", "disabled"):
            results = grouped[(case_id, condition)]
            if len(results) != TRIALS_PER_CONDITION:
                failures.append(f"{case_id}/{condition} needs {TRIALS_PER_CONDITION} trials")
                continue
            passed = sum(matches(case, result) for result in results)
            rates[condition] = passed / TRIALS_PER_CONDITION
            reports.append(f"{case_id}: {condition} pass rate {rates[condition]:.0%}")
            if condition == "enabled" and rates[condition] < ENABLED_THRESHOLD:
                failures.append(f"{case_id}/enabled is below {ENABLED_THRESHOLD:.0%}")
        if len(rates) == 2:
            reports.append(f"{case_id}: outcome delta {rates['enabled'] - rates['disabled']:+.0%}")
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
    print("PASS: isolated harness results meet the enabled-condition threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
