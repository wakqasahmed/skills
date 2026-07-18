#!/usr/bin/env python3
"""Offline outcome evaluator for synthetic agent-readiness storefront snapshots."""
import json
from pathlib import Path


REQUIRED_READ_SIGNALS = ("bot_access", "server_rendered", "product_json_ld", "price", "availability", "variants", "policy", "support")
BLOCKERS = {
    "bot_access": "AI_CRAWLER_BLOCKED",
    "server_rendered": "PRODUCT_NOT_IN_RAW_HTML",
    "product_json_ld": "PRODUCT_STRUCTURED_DATA_MISSING",
    "price": "PRICE_MISSING",
    "availability": "AVAILABILITY_MISSING",
    "variants": "VARIANT_COVERAGE_MISSING",
    "policy": "POLICY_CONTEXT_MISSING",
    "support": "SUPPORT_PATH_MISSING",
}
ACTIONABLE_BOUNDARIES = {"answer_only", "draft_return", "supervised_order"}


def outcome(signals: dict) -> dict:
    blockers = [BLOCKERS[key] for key in REQUIRED_READ_SIGNALS if not signals[key]]
    read_ready = not blockers
    if signals["action_boundary"] == "unknown":
        blockers.append("ACTION_BOUNDARY_UNKNOWN")
    action_ready = read_ready and signals["action_boundary"] in ACTIONABLE_BOUNDARIES
    return {"read_ready": read_ready, "action_ready": action_ready, "blockers": blockers}


def main() -> int:
    fixture = Path(__file__).parent / "fixtures" / "held-out.json"
    data = json.loads(fixture.read_text())
    if data["schema_version"] != 1 or data["split"] != "held-out" or len(data["cases"]) < 10:
        raise SystemExit("held-out fixture contract failed")
    failures = []
    for case in data["cases"]:
        actual = outcome(case["signals"])
        if actual != case["expected"]:
            failures.append(f"{case['name']}: expected {case['expected']}, got {actual}")
        else:
            print(f"PASS {case['name']}")
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
