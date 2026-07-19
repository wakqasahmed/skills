#!/usr/bin/env python3
"""Validate structured audit artifacts, never free-form response phrases."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

CASES = Path(__file__).parent / "held-out-cases.json"
TRIALS = 5
ENABLED_THRESHOLD = 0.8
MINIMUM_ENABLED_DELTA = 0.02
RUNNER_PROTOCOL_VERSION = "seo-aeo-geo-artifact-runner/v1"
RECORD_FIELDS = {"case_id", "condition", "trial", "model", "model_version", "harness_version", "runner_protocol_version", "skill_used", "audit_artifact"}


def grade_artifact(case: dict, artifact: object) -> bool:
    if not isinstance(artifact, dict):
        return False
    expected = case["expected"]
    if artifact.get("disposition") != expected["disposition"]:
        return False
    if expected["disposition"] == "route" and artifact.get("route") != expected.get("route"):
        return False
    findings = artifact.get("findings")
    recommendations = artifact.get("recommendations")
    evidence = artifact.get("evidence")
    if not all(isinstance(value, list) for value in (findings, recommendations, evidence)):
        return False
    finding_ids = {item.get("id") for item in findings if isinstance(item, dict)}
    recommendation_ids = {item.get("id") for item in recommendations if isinstance(item, dict)}
    evidence_sources = {item.get("source") for item in evidence if isinstance(item, dict)}
    return (set(expected["finding_ids"]) <= finding_ids and set(expected["recommendation_ids"]) <= recommendation_ids and set(expected["evidence_sources"]) <= evidence_sources)


def validate(records: list[dict]) -> tuple[list[str], list[str]]:
    cases = {case["id"]: case for case in json.loads(CASES.read_text())["cases"]}
    failures, reports, seen = [], [], set()
    grouped = defaultdict(list)
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
        elif key[0] not in cases or key[1] not in ("enabled", "disabled") or not isinstance(key[2], int) or not 1 <= key[2] <= TRIALS:
            failures.append(f"invalid record: {key}")
        elif key in seen:
            failures.append(f"duplicate record: {key}")
        elif not isinstance(record["model"], str) or not record["model"].strip() or not isinstance(record["model_version"], str) or not record["model_version"].strip() or not isinstance(record["harness_version"], str) or not record["harness_version"].strip() or record["runner_protocol_version"] != RUNNER_PROTOCOL_VERSION:
            failures.append(f"invalid metadata: {key}")
        elif record["skill_used"] is not (key[1] == "enabled" and cases[key[0]]["expected_skill_usage"] == "use"):
            failures.append(f"invalid skill_used: {key}")
        else:
            seen.add(key)
            grouped[key[:2]].append(record)
    totals = {condition: [0, 0] for condition in ("enabled", "disabled")}
    for case_id, case in cases.items():
        rates = {}
        for condition in totals:
            group = grouped[(case_id, condition)]
            if len(group) != TRIALS:
                failures.append(f"{case_id}/{condition} needs {TRIALS} trials")
                continue
            passed = sum(grade_artifact(case, record["audit_artifact"]) for record in group)
            totals[condition][0] += passed
            totals[condition][1] += TRIALS
            rates[condition] = passed / TRIALS
            reports.append(f"{case_id}: {condition} artifact pass rate {rates[condition]:.0%}")
            if condition == "enabled" and rates[condition] < ENABLED_THRESHOLD:
                failures.append(f"{case_id}/enabled is below {ENABLED_THRESHOLD:.0%}")
        if len(rates) == 2:
            reports.append(f"{case_id}: artifact outcome delta {rates['enabled'] - rates['disabled']:+.0%}")
    if all(totals[condition][1] for condition in totals):
        delta = totals["enabled"][0] / totals["enabled"][1] - totals["disabled"][0] / totals["disabled"][1]
        reports.append(f"aggregate artifact outcome delta {delta:+.0%}")
        if delta < MINIMUM_ENABLED_DELTA:
            failures.append(f"aggregate enabled artifact outcome delta is below {MINIMUM_ENABLED_DELTA:.0%}")
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
    print("PASS: isolated SEO/AEO/GEO artifact harness results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
