#!/usr/bin/env python3
"""Score synthetic harness outcomes without reimplementing launch policy."""
import argparse
import json
from collections import Counter
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures" / "held-out-scenarios.json"
REQUIRED_OUTCOME_FIELDS = {"decision", "reason_code", "required_actions"}
REQUIRED_CASE_FIELDS = {"name", "split", "prompt", "expected"}


def load_cases() -> tuple[list[dict], list[str]]:
    fixtures = json.loads(FIXTURES.read_text())
    cases = fixtures.get("cases", [])
    failures = []
    if fixtures.get("schema_version") != 1:
        failures.append("unsupported scenario schema")
    if len(cases) < 10:
        failures.append("fewer than 10 held-out scenarios")

    names = set()
    for case in cases:
        if not REQUIRED_CASE_FIELDS.issubset(case):
            failures.append("scenario is incomplete")
            continue
        if case["name"] in names:
            failures.append(f"{case['name']}: scenario name is duplicated")
            continue
        names.add(case["name"])
        if case["split"] != "held-out":
            failures.append(f"{case['name']}: scenario is not held-out")
        if not REQUIRED_OUTCOME_FIELDS.issubset(case["expected"]):
            failures.append(f"{case['name']}: expected outcome is incomplete")
    return cases, failures


def validate_records(records: list[dict], cases: list[dict], trials: int) -> tuple[list[str], dict]:
    expected = {case["name"]: case["expected"] for case in cases}
    required = {(name, condition, trial) for name in expected for condition in ("enabled", "disabled") for trial in range(trials)}
    keys = [(record.get("name"), record.get("condition"), record.get("trial")) for record in records]
    actual = set(keys)
    failures = []
    if actual != required or len(records) != len(required) or any(count != 1 for count in Counter(keys).values()):
        failures.append("harness records do not cover every case, condition, and trial exactly once")

    for record in records:
        name = record.get("name")
        if name in expected and not REQUIRED_OUTCOME_FIELDS.issubset(record.get("outcome", {})):
            failures.append(f"{name}: outcome is incomplete")

    summary = {}
    for condition in ("enabled", "disabled"):
        condition_records = [record for record in records if record.get("condition") == condition]
        passes = sum(record.get("outcome") == expected.get(record.get("name")) for record in condition_records)
        summary[f"{condition}_pass_rate"] = passes / len(condition_records) if condition_records else 0
    summary["delta"] = summary["enabled_pass_rate"] - summary["disabled_pass_rate"]
    return failures, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path)
    parser.add_argument("--validate-fixtures", action="store_true")
    parser.add_argument("--trials", type=int, choices=range(1, 7), default=1)
    args = parser.parse_args()
    if bool(args.results) == args.validate_fixtures:
        parser.error("provide exactly one of --results or --validate-fixtures")

    cases, failures = load_cases()
    summary = {"delta": 0}
    if args.results:
        results = json.loads(args.results.read_text())
        records = results.get("records", [])
        record_failures, summary = validate_records(records, cases, args.trials)
        failures.extend(record_failures)

    if failures:
        print("FAIL: outcome scenarios")
        print("\n".join(failures))
        return 1
    print(f"PASS: {len(cases)} held-out outcome scenarios; delta={summary['delta']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
