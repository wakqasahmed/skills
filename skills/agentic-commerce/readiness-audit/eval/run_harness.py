#!/usr/bin/env python3
"""Run readiness-audit cases in clean, network-isolated workspaces."""
import argparse
import hashlib
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
RUNNER_PROTOCOL_VERSION = "readiness-audit-runner/v2"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_workspace(workspace: Path, runner: Path, case: dict, condition: str) -> dict:
    (workspace / "case.json").write_text(json.dumps({"id": case["id"], "prompt": case["prompt"]}))
    shutil.copy2(EVAL_DIR / case["fixture"], workspace / "fixture.html")
    shutil.copy2(runner, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL_DIR.parent / "SKILL.md", workspace / "SKILL.md")
    files = ["case.json", "fixture.html", *(["SKILL.md"] if condition == "enabled" else [])]
    check = {"protocol_version": RUNNER_PROTOCOL_VERSION, "files": files, "sha256": {name: digest(workspace / name) for name in files}}
    (workspace / "input-check.json").write_text(json.dumps(check))
    return check


def isolated_command(workspace: Path, image: str, model: str, condition: str, trial: int) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HOME=/nonexistent", "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", "HARNESS_FIXTURE=/workspace/fixture.html", "--env", f"HARNESS_MODEL={model}",
        "--env", f"HARNESS_CONDITION={condition}", "--env", f"HARNESS_TRIAL={trial}",
        "--workdir", "/workspace", image, "/workspace/runner",
        "--case", "/workspace/case.json", "--fixture", "/workspace/fixture.html",
        "--check", "/workspace/input-check.json",
        *(["--skill", "/workspace/SKILL.md"] if condition == "enabled" else []),
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
                    input_check = prepare_workspace(workspace, runner, case, condition)
                    result = subprocess.run(isolated_command(workspace, args.image, args.model, condition, trial), text=True, capture_output=True, check=True, env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"})
                try:
                    record = json.loads(result.stdout)
                except json.JSONDecodeError as error:
                    raise SystemExit(f"runner must emit one JSON object per case/trial: {error}") from error
                if not isinstance(record, dict) or record.get("protocol_version") != RUNNER_PROTOCOL_VERSION:
                    raise SystemExit(f"runner must use {RUNNER_PROTOCOL_VERSION}")
                if record.get("loaded_files") != input_check["files"] or not isinstance(record.get("target_response"), str) or not record["target_response"].strip():
                    raise SystemExit("runner must confirm the exact passed inputs and emit a non-empty target_response")
                records.append({"case_id": case["id"], "condition": condition, "trial": trial, "model": args.model, "harness_version": HARNESS_VERSION, "runner_protocol_version": RUNNER_PROTOCOL_VERSION, "execution": {"exit_code": result.returncode, "provided_inputs": input_check, "loaded_files": record["loaded_files"]}, "target_response": record["target_response"]})
    args.output.write_text(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
