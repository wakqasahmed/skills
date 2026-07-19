#!/usr/bin/env python3
"""Versioned target-agent invocation contract for the isolated image."""
import json
import os
import subprocess
from pathlib import Path


workspace = Path(os.environ["HARNESS_WORKSPACE"])
request = workspace / "request.json"
output = Path("/tmp/outcome.json")
command = [
    "/opt/marketplace-agent/bin/agent", "--model", os.environ["HARNESS_MODEL"],
    "--request", str(request), "--repository", str(workspace / "repository"),
    "--output", str(output), "--trial", os.environ["HARNESS_TRIAL"],
]
if (workspace / "SKILL.md").is_file():
    command.extend(("--skill", str(workspace / "SKILL.md")))
subprocess.run(command, check=True)
artifact = json.loads(output.read_text())
if not isinstance(artifact, dict):
    raise SystemExit("target agent output must be a JSON object")
print(json.dumps(artifact))
