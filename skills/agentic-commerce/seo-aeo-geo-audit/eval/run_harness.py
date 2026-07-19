#!/usr/bin/env python3
"""Run audit agents in isolated workspaces for enabled/disabled ablation."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
CASES = EVAL_DIR / "held-out-cases.json"
TARGET_AGENT = EVAL_DIR / "run_target_agent.py"
HARNESS_VERSION = "seo-aeo-geo-isolated-harness/v1"
RUNNER_PROTOCOL_VERSION = "seo-aeo-geo-artifact-runner/v1"


def prepare_workspace(workspace: Path, case: dict, condition: str) -> None:
    (workspace / "case.json").write_text(json.dumps({"id": case["id"], "prompt": case["prompt"], "input": case["input"]}))
    shutil.copy2(TARGET_AGENT, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL_DIR.parent / "SKILL.md", workspace / "SKILL.md")
        shutil.copy2(EVAL_DIR.parent / "references" / "checks.md", workspace / "checks.md")


def isolated_command(workspace: Path, image: str, model: str, condition: str, trial: int) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HOME=/nonexistent", "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_MODEL={model}", "--env", f"HARNESS_CONDITION={condition}",
        "--env", f"HARNESS_TRIAL={trial}", "--workdir", "/workspace", image, "/workspace/runner",
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
                    result = subprocess.run(isolated_command(workspace, args.image, args.model, condition, trial), text=True, capture_output=True, check=True, env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"})
                try:
                    runner_record = json.loads(result.stdout)
                except json.JSONDecodeError as error:
                    raise SystemExit(f"runner must emit one JSON object: {error}") from error
                if runner_record.get("protocol_version") != RUNNER_PROTOCOL_VERSION or not isinstance(runner_record.get("skill_used"), bool) or not isinstance(runner_record.get("audit_artifact"), dict):
                    raise SystemExit(f"runner must emit {RUNNER_PROTOCOL_VERSION}, skill_used, and an audit_artifact object")
                records.append({"case_id": case["id"], "condition": condition, "trial": trial, "model": args.model, "harness_version": HARNESS_VERSION, "runner_protocol_version": RUNNER_PROTOCOL_VERSION, "skill_used": runner_record["skill_used"], "audit_artifact": runner_record["audit_artifact"]})
    args.output.write_text(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
