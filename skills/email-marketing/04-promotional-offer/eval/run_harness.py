#!/usr/bin/env python3
"""Run a supplied agent harness in isolated skill-enabled and disabled workspaces."""
import argparse
from collections import Counter
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EVAL = Path(__file__).parent
FIXTURES = EVAL / "fixtures" / "held-out-scenarios.json"
PASS_RATE_THRESHOLD = 0.8
CONFIG = EVAL / "harness-config.json"

if str(EVAL) not in sys.path:
    sys.path.insert(0, str(EVAL))

from evaluate_outcomes import score


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text())
    image = config.get("image", "")
    if "@sha256:" not in image:
        raise ValueError("harness image must be pinned to an immutable digest")
    if not isinstance(config.get("runner"), str) or not config.get("expected_metadata"):
        raise ValueError("harness config must declare a runner and expected metadata")
    return config


def validate_metadata(metadata: dict, expected: dict) -> None:
    if metadata != expected:
        raise ValueError("runner metadata does not match the repository-controlled configuration")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(records: list[dict], cases: list[dict], trials: int) -> dict:
    required = {
        (case["name"], condition, trial)
        for case in cases
        for condition in ("enabled", "disabled")
        for trial in range(trials)
    }
    record_keys = [
        (record.get("name"), record.get("condition"), record.get("trial"))
        for record in records
    ]
    duplicate_records = any(count != 1 for count in Counter(record_keys).values())
    if set(record_keys) != required or len(records) != len(required) or duplicate_records:
        raise ValueError("harness records do not cover every case, condition, and trial exactly once")

    enabled = [record for record in records if record["condition"] == "enabled"]
    disabled = [record for record in records if record["condition"] == "disabled"]
    enabled_passes, enabled_failures = score(enabled, cases)
    disabled_passes, disabled_failures = score(disabled, cases)
    if enabled_failures or disabled_failures:
        raise ValueError("harness returned invalid outcome records")
    return {
        "enabled_pass_rate": enabled_passes / len(enabled),
        "disabled_pass_rate": disabled_passes / len(disabled),
        "delta": (enabled_passes - disabled_passes) / len(enabled),
    }


def prepare_workspace(workspace: Path, runner: Path, condition: str) -> None:
    cases = json.loads(FIXTURES.read_text())["cases"]
    prompts = {"cases": [{"name": case["name"], "prompt": case["prompt"]} for case in cases]}
    (workspace / "cases.json").write_text(json.dumps(prompts))
    shutil.copy2(runner, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, condition: str, trial: int) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_CONDITION={condition}",
        "--env", f"HARNESS_TRIAL={trial}",
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def build_report(
    trials: int,
    metadata: dict,
    runner_sha256: str,
    summary: dict,
    records: list[dict],
) -> dict:
    return {
        "trials": trials,
        "model_version": metadata["model_version"],
        "harness_version": metadata["harness_version"],
        "runner_sha256": runner_sha256,
        "summary": summary,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    runner = (Path.cwd() / config["runner"]).resolve()
    if not runner.is_file() or not runner.is_relative_to(Path.cwd()):
        raise SystemExit("runner must be a repository-controlled file")
    runner_sha256 = file_sha256(runner)
    if runner_sha256 != config.get("runner_sha256"):
        raise SystemExit("runner does not match the repository-controlled digest")

    cases = json.loads(FIXTURES.read_text())["cases"]
    records = []
    for condition in ("enabled", "disabled"):
        for trial in range(args.trials):
            with tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                prepare_workspace(workspace, runner, condition)
                result = subprocess.run(
                    isolated_command(workspace, config["image"], condition, trial),
                    text=True,
                    capture_output=True,
                    env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"},
                    check=True,
                )
                output = json.loads(result.stdout)
                validate_metadata(output.get("metadata"), config["expected_metadata"])
                records.extend(output.get("records", []))

    summary = validate(records, cases, args.trials)
    if summary["enabled_pass_rate"] < PASS_RATE_THRESHOLD or summary["delta"] <= 0:
        raise SystemExit(f"harness gate failed: {summary}")
    report = build_report(args.trials, config["expected_metadata"], runner_sha256, summary, records)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
