#!/usr/bin/env python3
"""Score observable event-campaign outcomes against an independent answer key."""
import json
from pathlib import Path


EVAL = Path(__file__).parent
FIXTURES = EVAL / "fixtures"
PROMPTS = FIXTURES / "held-out-prompts.json"
OUTCOME_KEY = FIXTURES / "outcome-key.json"
CANDIDATES = FIXTURES / "candidate-outcomes.json"


def score_records(records: list[dict], cases: list[dict], outcomes: dict[str, dict]) -> dict:
    case_names = {case["name"] for case in cases}
    if set(outcomes) != case_names:
        raise ValueError("outcome key must cover each held-out prompt exactly once")
    by_name = {record.get("name"): record.get("outcome") for record in records}
    if len(records) != len(by_name) or set(by_name) != case_names:
        raise ValueError("outcome records must cover each held-out prompt exactly once")

    passed = sum(all(by_name[name].get(field) == value for field, value in expected.items()) for name, expected in outcomes.items())
    total = len(outcomes)
    return {"passed": passed, "total": total, "pass_rate": passed / total}


def main() -> int:
    cases = json.loads(PROMPTS.read_text())["cases"]
    outcomes = json.loads(OUTCOME_KEY.read_text())["outcomes"]
    records = json.loads(CANDIDATES.read_text())["records"]
    summary = score_records(records, cases, outcomes)
    if summary["passed"] != summary["total"]:
        print(f"FAIL: held-out event outcomes: {summary}")
        return 1
    print(f"PASS: {summary['passed']} held-out event outcomes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
