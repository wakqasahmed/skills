#!/usr/bin/env python3
"""Independently grade structured product-knowledge outcome artifacts."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


CASES = Path(__file__).parent / "held-out-cases.json"
TRIALS = 5
ENABLED_THRESHOLD = 0.8
MINIMUM_ENABLED_DELTA = 0.02
GRADER_VERSION = "product-knowledge-outcome-grader/v2"
RUNNER_PROTOCOL_VERSION = "product-knowledge-outcome-runner/v2"
RECORD_FIELDS = {"case_id", "condition", "trial", "model", "harness_version", "runner_protocol_version", "artifact"}


def grade_artifact(case: dict, artifact: object) -> bool:
    return artifact == case["expected_artifact"]


def validate(records: list[dict]) -> tuple[list[str], list[str]]:
    cases = {case["id"]: case for case in json.loads(CASES.read_text())["cases"]}
    failures, reports, seen = [], [], set()
    grouped = defaultdict(list)
    totals = {condition: [0, 0] for condition in ("enabled", "disabled")}
    if not isinstance(records, list):
        return ["results must be a list"], reports
    for record in records:
        if not isinstance(record, dict):
            failures.append("record must be an object")
            continue
        key = (record.get("case_id"), record.get("condition"), record.get("trial"))
        missing = RECORD_FIELDS - record.keys()
        if missing:
            failures.append(f"{key} missing fields: {sorted(missing)}")
        elif key[0] not in cases or key[1] not in totals or not isinstance(key[2], int) or not 1 <= key[2] <= TRIALS:
            failures.append(f"invalid record: {key}")
        elif key in seen:
            failures.append(f"duplicate record: {key}")
        elif (not isinstance(record["model"], str) or not record["model"].strip()
              or not isinstance(record["harness_version"], str) or not record["harness_version"].strip()
              or record["runner_protocol_version"] != RUNNER_PROTOCOL_VERSION):
            failures.append(f"invalid metadata: {key}")
        else:
            seen.add(key)
            grouped[key[:2]].append(record)

    for case_id, case in cases.items():
        rates = {}
        for condition in totals:
            result_set = grouped[(case_id, condition)]
            if len(result_set) != TRIALS:
                failures.append(f"{case_id}/{condition} needs {TRIALS} trials")
                continue
            passes = sum(grade_artifact(case, record["artifact"]) for record in result_set)
            totals[condition][0] += passes
            totals[condition][1] += TRIALS
            rates[condition] = passes / TRIALS
            reports.append(f"{case_id}: {condition} artifact pass rate {rates[condition]:.0%}")
            if condition == "enabled" and rates[condition] < ENABLED_THRESHOLD:
                failures.append(f"{case_id}/enabled is below {ENABLED_THRESHOLD:.0%}")
        if len(rates) == 2:
            reports.append(f"{case_id}: artifact delta {rates['enabled'] - rates['disabled']:+.0%}")

    if all(totals[condition][1] for condition in totals):
        outcome_delta = totals["enabled"][0] / totals["enabled"][1] - totals["disabled"][0] / totals["disabled"][1]
        reports.append(f"aggregate artifact delta {outcome_delta:+.0%}")
        if outcome_delta < MINIMUM_ENABLED_DELTA:
            failures.append(f"aggregate enabled artifact delta is below {MINIMUM_ENABLED_DELTA:.0%}")
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
    print(f"PASS: isolated product-knowledge harness results ({GRADER_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
