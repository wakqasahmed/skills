#!/usr/bin/env python3
"""Adapter for the target agent baked into the pinned evaluator image."""
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


PROTOCOL_VERSION = "seo-aeo-geo-artifact-runner/v1"
DEFAULT_TARGET_AGENT = "/usr/local/bin/seo-aeo-geo-audit-agent"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MAX_ATTEMPTS = 5


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


def workspace_request(workspace: Path, model: str) -> dict:
    target_input = json.loads((workspace / "input.json").read_text())
    request = {
        "protocol_version": PROTOCOL_VERSION,
        "model": model,
        "prompt": target_input["prompt"],
        "input": target_input["input"],
    }
    if (workspace / "SKILL.md").is_file():
        request["skill"] = (workspace / "SKILL.md").read_text()
        request["checks"] = (workspace / "checks.md").read_text()
    return request


def run_target_agent(request: dict, command: str) -> dict:
    result = subprocess.run(
        [command, "--model", request["model"]],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=True,
    )
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(f"target agent must emit one JSON object: {error}") from error
    if not isinstance(response, dict):
        raise SystemExit("target agent must emit one JSON object")
    return response


def rate_limit_delay(headers: object, attempt: int) -> int:
    retry_after = headers.get("Retry-After") if headers else None
    if retry_after and retry_after.isdigit():
        return int(retry_after)
    reset_at = headers.get("X-RateLimit-Reset") if headers else None
    if reset_at and reset_at.isdigit():
        return max(1, int(int(reset_at) / 1000 - time.time()))
    return 2 ** attempt


def run_openrouter_agent(request: dict) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is required for the openrouter runner")
    instructions = "Return exactly one JSON object with a boolean skill_used and an audit_artifact object."
    if "skill" in request:
        instructions += f"\n\nSKILL.md:\n{request['skill']}\n\nchecks.md:\n{request['checks']}"
    body = json.dumps({
        "model": request["model"],
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": json.dumps({"prompt": request["prompt"], "input": request["input"]})},
        ],
        "response_format": {"type": "json_object"},
    }).encode()
    http_request = urllib.request.Request(
        OPENROUTER_API_URL,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(OPENROUTER_MAX_ATTEMPTS):
        try:
            with urllib.request.build_opener(NoRedirect()).open(http_request, timeout=120) as response:
                payload = json.loads(response.read())
            break
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == OPENROUTER_MAX_ATTEMPTS - 1:
                raise SystemExit(f"OpenRouter request failed: HTTP {error.code}") from error
            time.sleep(rate_limit_delay(error.headers, attempt))
        except (urllib.error.URLError, json.JSONDecodeError) as error:
            raise SystemExit(f"OpenRouter request failed: {error}") from error
    try:
        response = json.loads(payload["choices"][0]["message"]["content"])
    except (IndexError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit(f"OpenRouter must return a JSON audit artifact: {error}") from error
    if not isinstance(response, dict) or not isinstance(response.get("skill_used"), bool) or not isinstance(response.get("audit_artifact"), dict):
        raise SystemExit("OpenRouter must return skill_used and an audit_artifact object")
    return {
        "model": request["model"],
        "model_version": os.environ["HARNESS_MODEL_VERSION"],
        "skill_used": response["skill_used"],
        "audit_artifact": response["audit_artifact"],
    }


def main() -> int:
    workspace = Path(os.environ.get("HARNESS_WORKSPACE", "/workspace"))
    model = os.environ["HARNESS_MODEL"]
    request = workspace_request(workspace, model)
    if os.environ.get("HARNESS_RUNNER", "isolated") == "openrouter":
        response = run_openrouter_agent(request)
    else:
        response = run_target_agent(request, os.environ.get("TARGET_AGENT_COMMAND", DEFAULT_TARGET_AGENT))
    if response.get("model") != model or not isinstance(response.get("model_version"), str) or not response["model_version"].strip():
        raise SystemExit("target agent must attest the requested model and a non-empty model_version")
    if not isinstance(response.get("skill_used"), bool) or not isinstance(response.get("audit_artifact"), dict):
        raise SystemExit("target agent must emit skill_used and an audit_artifact object")
    print(json.dumps({
        "protocol_version": PROTOCOL_VERSION,
        "model": response["model"],
        "model_version": response["model_version"],
        "skill_used": response["skill_used"],
        "audit_artifact": response["audit_artifact"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
