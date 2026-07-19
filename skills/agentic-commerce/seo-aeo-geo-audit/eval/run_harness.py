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


def prepare_workspace(workspace: Path, case: dict, condition: str) -> Path:
    target_workspace = workspace / "target-input"
    target_workspace.mkdir(parents=True)
    (target_workspace / "input.json").write_text(json.dumps({"prompt": case["prompt"], "input": case["input"]}))
    shutil.copy2(TARGET_AGENT, target_workspace / "runner")
    (target_workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL_DIR.parent / "SKILL.md", target_workspace / "SKILL.md")
        shutil.copy2(EVAL_DIR.parent / "references" / "checks.md", target_workspace / "checks.md")
    return target_workspace


def isolated_command(workspace: Path, image: str, model: str) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HOME=/nonexistent", "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_MODEL={model}", "--workdir", "/workspace", image, "/workspace/runner",
    ]


def openrouter_command(workspace: Path) -> list[str]:
    return ["python3", str(workspace / "runner")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", choices=("isolated", "openrouter"), default="isolated")
    parser.add_argument("--image")
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-version")
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.runner == "isolated" and (not args.image or "@sha256:" not in args.image):
        raise SystemExit("image must be pinned by digest")
    if args.runner == "openrouter" and not args.model_version:
        raise SystemExit("--model-version is required for the openrouter runner")

    records = []
    for case in json.loads(CASES.read_text())["cases"]:
        for condition in ("enabled", "disabled"):
            for trial in range(1, args.trials + 1):
                with tempfile.TemporaryDirectory() as directory:
                    workspace = Path(directory)
                    target_workspace = prepare_workspace(workspace, case, condition)
                    environment = {"PATH": os.environ["PATH"], "HOME": "/nonexistent", "HARNESS_WORKSPACE": str(target_workspace), "HARNESS_MODEL": args.model, "HARNESS_RUNNER": args.runner}
                    if args.runner == "openrouter":
                        environment["HARNESS_MODEL_VERSION"] = args.model_version
                        environment["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "")
                        command = openrouter_command(target_workspace)
                    else:
                        command = isolated_command(target_workspace, args.image, args.model)
                    result = subprocess.run(command, text=True, capture_output=True, check=True, env=environment)
                try:
                    runner_record = json.loads(result.stdout)
                except json.JSONDecodeError as error:
                    raise SystemExit(f"runner must emit one JSON object: {error}") from error
                if runner_record.get("protocol_version") != RUNNER_PROTOCOL_VERSION or runner_record.get("model") != args.model or not isinstance(runner_record.get("model_version"), str) or not runner_record["model_version"].strip() or not isinstance(runner_record.get("skill_used"), bool) or not isinstance(runner_record.get("audit_artifact"), dict):
                    raise SystemExit(f"runner must emit {RUNNER_PROTOCOL_VERSION}, the declared model and version, skill_used, and an audit_artifact object")
                records.append({"case_id": case["id"], "condition": condition, "trial": trial, "model": runner_record["model"], "model_version": runner_record["model_version"], "harness_version": HARNESS_VERSION, "runner_protocol_version": RUNNER_PROTOCOL_VERSION, "skill_used": runner_record["skill_used"], "audit_artifact": runner_record["audit_artifact"]})
    args.output.write_text(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
