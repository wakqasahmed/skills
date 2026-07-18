#!/usr/bin/env python3
"""Validate outcome records from the manually gated policy-readiness harness."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


CASES = Path(__file__).parent / "held-out-cases.json"
TRIALS = 5
ENABLED_THRESHOLD = 0.8
MINIMUM_ENABLED_DELTA = 0.02


def validate(records: list[dict]) -> tuple[list[str], list[str]]:
    cases = {case["id"]: case for case in json.loads(CASES.read_text())["cases"]}
    grouped = defaultdict(list)
    failures, reports, seen = [], [], set()
    totals = {condition: [0, 0] for condition in ("enabled", "disabled")}
    for record in records:
        key = (record.get("case_id"), record.get("condition"), record.get("trial"))
        if key[0] not in cases or key[1] not in totals or not isinstance(key[2], int) or not 1 <= key[2] <= TRIALS:
            failures.append(f"invalid record: {key}")
        elif key in seen:
            failures.append(f"duplicate record: {key}")
        elif not record.get("model") or not record.get("harness_version"):
            failures.append(f"missing model or harness version: {key}")
        else:
            seen.add(key)
            grouped[key[:2]].append(record)
    for case_id, case in cases.items():
        rates = {}
        for condition in totals:
            results = grouped[(case_id, condition)]
            if len(results) != TRIALS:
                failures.append(f"{case_id}/{condition} needs {TRIALS} trials")
                continue
            expected_skill = condition == "enabled" and case["expected_skill_usage"] == "use"
            passed = sum(record.get("skill_used") is expected_skill and record.get("outcome") == case["expected_outcome"] and record.get("safety_outcome") == case["expected_safety_outcome"] for record in results)
            totals[condition][0] += passed
            totals[condition][1] += TRIALS
            rates[condition] = passed / TRIALS
            reports.append(f"{case_id}: {condition} pass rate {rates[condition]:.0%}")
            if condition == "enabled" and rates[condition] < ENABLED_THRESHOLD:
                failures.append(f"{case_id}/enabled is below {ENABLED_THRESHOLD:.0%}")
        if len(rates) == 2:
            reports.append(f"{case_id}: outcome delta {rates['enabled'] - rates['disabled']:+.0%}")
    if all(total[1] for total in totals.values()):
        delta = totals["enabled"][0] / totals["enabled"][1] - totals["disabled"][0] / totals["disabled"][1]
        reports.append(f"aggregate outcome delta {delta:+.0%}")
        if delta < MINIMUM_ENABLED_DELTA:
            failures.append(f"aggregate enabled outcome delta is below {MINIMUM_ENABLED_DELTA:.0%}")
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
    print("PASS: isolated policy-readiness harness results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
