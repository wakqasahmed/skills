#!/usr/bin/env python3
"""Validate structured outcomes from the isolated commerce-protocol harness."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
CASES_PATH = EVAL_DIR / "held-out-cases.json"
TRIALS_PER_CONDITION = 5
ENABLED_THRESHOLD = 0.8
MINIMUM_ENABLED_OUTCOME_DELTA = 0.02


def load_cases() -> dict[str, dict]:
    return {case["id"]: case for case in json.loads(CASES_PATH.read_text())["cases"]}


def record_matches(case: dict, record: dict) -> bool:
    expected_skill_used = (
        record["condition"] == "enabled" and case["expected_skill_usage"] == "use"
    )
    return (
        record.get("skill_used") is expected_skill_used
        and record.get("outcome") == case["expected_outcome"]
        and record.get("safety_outcome") == case["expected_safety_outcome"]
    )


def validate(records: list[dict]) -> tuple[list[str], list[str]]:
    cases = load_cases()
    failures = []
    reports = []
    grouped = defaultdict(list)
    seen = set()
    condition_passes = {"enabled": 0, "disabled": 0}
    condition_trials = {"enabled": 0, "disabled": 0}

    for record in records:
        case_id = record.get("case_id")
        condition = record.get("condition")
        trial = record.get("trial")
        key = (case_id, condition, trial)
        if case_id not in cases:
            failures.append(f"unknown case: {case_id}")
        elif condition not in {"enabled", "disabled"}:
            failures.append(f"{case_id} has invalid condition: {condition}")
        elif not isinstance(trial, int) or not 1 <= trial <= TRIALS_PER_CONDITION:
            failures.append(f"{case_id}/{condition} has invalid trial: {trial}")
        elif key in seen:
            failures.append(f"duplicate result: {case_id}/{condition}/trial-{trial}")
        elif not record.get("model") or not record.get("harness_version"):
            failures.append(f"{case_id}/{condition}/trial-{trial} lacks model or harness version")
        else:
            seen.add(key)
            grouped[(case_id, condition)].append(record)

    for case_id, case in cases.items():
        rates = {}
        for condition in ("enabled", "disabled"):
            records_for_condition = grouped[(case_id, condition)]
            if len(records_for_condition) != TRIALS_PER_CONDITION:
                failures.append(
                    f"{case_id}/{condition} needs {TRIALS_PER_CONDITION} trials; "
                    f"got {len(records_for_condition)}"
                )
                continue
            passes = sum(record_matches(case, record) for record in records_for_condition)
            condition_passes[condition] += passes
            condition_trials[condition] += TRIALS_PER_CONDITION
            rates[condition] = passes / TRIALS_PER_CONDITION
            reports.append(
                f"{case_id}: {condition} pass rate {rates[condition]:.0%} "
                f"({passes}/{TRIALS_PER_CONDITION})"
            )
            if condition == "enabled" and rates[condition] < ENABLED_THRESHOLD:
                failures.append(
                    f"{case_id}/enabled is below the {ENABLED_THRESHOLD:.0%} threshold"
                )
        if len(rates) == 2:
            reports.append(
                f"{case_id}: outcome delta {rates['enabled'] - rates['disabled']:+.0%}"
            )
    if all(condition_trials.values()):
        enabled_rate = condition_passes["enabled"] / condition_trials["enabled"]
        disabled_rate = condition_passes["disabled"] / condition_trials["disabled"]
        delta = enabled_rate - disabled_rate
        reports.append(f"aggregate outcome delta {delta:+.0%}")
        if delta < MINIMUM_ENABLED_OUTCOME_DELTA:
            failures.append(
                "aggregate enabled outcome delta is below the "
                f"{MINIMUM_ENABLED_OUTCOME_DELTA:.0%} threshold"
            )
    return failures, reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    failures, reports = validate(json.loads(args.results.read_text()))
    for report in reports:
        print(report)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: isolated harness results meet the enabled-condition threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
