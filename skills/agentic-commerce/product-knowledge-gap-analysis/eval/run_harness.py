#!/usr/bin/env python3
"""Run a repository-controlled product-knowledge evaluator in isolated workspaces."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
CASES = EVAL_DIR / "held-out-cases.json"
HARNESS_VERSION = "1"
RUNNER_PROTOCOL_VERSION = "product-knowledge-outcome-runner/v2"
RUNNER = EVAL_DIR / "runner.py"
TRIAL_TIMEOUT_SECONDS = 30


def executor_case(case: dict) -> dict:
    return {key: case[key] for key in ("id", "prompt", "catalog", "feed")}


def prepare_workspace(workspace: Path, case: dict, condition: str) -> None:
    (workspace / "case.json").write_text(json.dumps(executor_case(case)))
    shutil.copy2(RUNNER, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL_DIR.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, model: str) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HOME=/nonexistent",
        "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_MODEL={model}",
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if "@sha256:" not in args.image:
        raise SystemExit("image must be pinned by digest")

    records = []
    for case in json.loads(CASES.read_text())["cases"]:
        for condition in ("enabled", "disabled"):
            for trial in range(1, args.trials + 1):
                with tempfile.TemporaryDirectory() as directory:
                    workspace = Path(directory)
                    prepare_workspace(workspace, case, condition)
                    result = subprocess.run(
                        isolated_command(workspace, args.image, args.model),
                        text=True,
                        capture_output=True,
                        check=True,
                        timeout=TRIAL_TIMEOUT_SECONDS,
                        env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"},
                    )
                try:
                    record = json.loads(result.stdout)
                except json.JSONDecodeError as error:
                    raise SystemExit(f"runner must emit one JSON object per case/trial: {error}") from error
                if not isinstance(record, dict) or record.get("protocol_version") != RUNNER_PROTOCOL_VERSION:
                    raise SystemExit(f"runner must use {RUNNER_PROTOCOL_VERSION}")
                artifact = record.get("artifact")
                if not isinstance(artifact, dict):
                    raise SystemExit("runner must emit an artifact object")
                records.append({
                    "case_id": case["id"], "condition": condition, "trial": trial,
                    "model": args.model, "harness_version": HARNESS_VERSION,
                    "runner_protocol_version": RUNNER_PROTOCOL_VERSION, "artifact": artifact,
                })
    args.output.write_text(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
