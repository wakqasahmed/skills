#!/usr/bin/env python3
"""Run a repository-controlled FDE evaluator in disposable isolated workspaces."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parents[3]
CASES = EVAL_DIR / "held-out-cases.json"
HARNESS_VERSION = "1"
RUNNER_PROTOCOL_VERSION = "fde-outcome-runner/v1"


def prepare_workspace(workspace: Path, runner: Path, case: dict, condition: str) -> None:
    (workspace / "case.json").write_text(json.dumps({"id": case["id"], "prompt": case["prompt"]}))
    shutil.copy2(runner, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL_DIR.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, model: str, condition: str, trial: int) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HOME=/nonexistent",
        "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_MODEL={model}",
        "--env", f"HARNESS_CONDITION={condition}",
        "--env", f"HARNESS_TRIAL={trial}",
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runner = args.runner.resolve()
    if not runner.is_file() or not runner.is_relative_to(ROOT):
        raise SystemExit("runner must be a repository-controlled file")
    if "@sha256:" not in args.image:
        raise SystemExit("image must be pinned by digest")

    records = []
    for case in json.loads(CASES.read_text())["cases"]:
        for condition in ("enabled", "disabled"):
            for trial in range(1, args.trials + 1):
                with tempfile.TemporaryDirectory() as directory:
                    workspace = Path(directory)
                    prepare_workspace(workspace, runner, case, condition)
                    result = subprocess.run(
                        isolated_command(workspace, args.image, args.model, condition, trial),
                        text=True,
                        capture_output=True,
                        check=True,
                        env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"},
                    )
                try:
                    record = json.loads(result.stdout)
                except json.JSONDecodeError as error:
                    raise SystemExit(f"runner must emit one JSON object per case/trial: {error}") from error
                if not isinstance(record, dict):
                    raise SystemExit("runner must emit one JSON object per case/trial")
                if record.get("protocol_version") != RUNNER_PROTOCOL_VERSION:
                    raise SystemExit(f"runner must use {RUNNER_PROTOCOL_VERSION}")
                target_response = record.get("target_response")
                if not isinstance(target_response, str) or not target_response.strip():
                    raise SystemExit("runner must emit a non-empty target_response")
                records.append({
                    "case_id": case["id"],
                    "condition": condition,
                    "trial": trial,
                    "model": args.model,
                    "harness_version": HARNESS_VERSION,
                    "runner_protocol_version": RUNNER_PROTOCOL_VERSION,
                    "target_response": target_response,
                })
    args.output.write_text(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
