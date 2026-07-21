#!/usr/bin/env python3
"""Exercise the versioned local runner output interface without Docker or a model."""
import importlib.util
import json
from pathlib import Path
import tempfile


EVAL = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("newsletter_harness", EVAL / "run_harness.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def records(cases: list[dict], trials: int) -> list[dict]:
    return [
        {
            "case_id": case["case_id"],
            "condition": condition,
            "trial": trial,
            "outcome": case["expected"],
            "runner_version": "fixture-runner/v1",
            "model": "fixture-model/v1",
        }
        for case in cases
        for condition in ("enabled", "disabled")
        for trial in range(trials)
    ]


def main() -> int:
    cases = json.loads((EVAL / "fixtures" / "held-out-scenarios.json").read_text())["cases"]
    summary = MODULE.validate(records(cases, 3), cases, 3, "fixture-runner/v1", "fixture-model/v1")
    if summary["enabled_pass_rate"] != 1 or summary["disabled_pass_rate"] != 1:
        raise SystemExit("fixture output interface did not validate")

    invalid = records(cases, 3)
    invalid[0]["model"] = "unversioned-model"
    try:
        MODULE.validate(invalid, cases, 3, "fixture-runner/v1", "fixture-model/v1")
    except ValueError:
        pass
    else:
        raise SystemExit("runner output version mutation was accepted")

    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        MODULE.prepare_workspace(workspace, EVAL / "run-eval.sh", "disabled")
        runner_cases = json.loads((workspace / "cases.json").read_text())
        if set(runner_cases) != {"schema_version", "cases"}:
            raise SystemExit("runner input schema leaked evaluator fields")
        if any(set(case) != {"case_id", "prompt"} for case in runner_cases["cases"]):
            raise SystemExit("runner workspace leaked expected outcomes")
        if [case["case_id"] for case in runner_cases["cases"]] != [case["case_id"] for case in cases]:
            raise SystemExit("runner inputs do not match evaluator case IDs")
        if any(
            not case["case_id"].startswith("case-")
            or not case["case_id"].removeprefix("case-").isdigit()
            for case in runner_cases["cases"]
        ):
            raise SystemExit("runner case IDs are not opaque")
        if (workspace / "SKILL.md").exists():
            raise SystemExit("disabled workspace leaked the skill")
        command = MODULE.isolated_command(
            workspace, "example@sha256:fixture", "disabled", 0, "fixture-runner/v1", "fixture-model/v1"
        )
        if any("HARNESS_CONDITION" in value for value in command):
            raise SystemExit("runner command leaked the ablation condition")

        enabled_workspace = Path(directory) / "enabled"
        enabled_workspace.mkdir()
        MODULE.prepare_workspace(enabled_workspace, EVAL / "run-eval.sh", "enabled")
        if not (enabled_workspace / "SKILL.md").exists():
            raise SystemExit("enabled workspace omitted the skill")

    print("PASS: versioned local runner output interface and blinded answer-key isolation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
