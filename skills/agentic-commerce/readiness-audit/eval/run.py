#!/usr/bin/env python3
"""Behavioral eval runner for the readiness-audit skill.

Runs the readiness-audit skill (as an LLM system prompt) against the frozen
fixtures in eval/fixtures/*.html and asserts that the resulting audit meets
the skill's own structural contract: six dimensions scored 0-3 with cited
evidence, exactly one routing outcome, and no analytics/Search Console
claims without verified exports.

Requires ANTHROPIC_API_KEY (real token cost) -- see the README section
"Behavioral eval for readiness-audit" for how to run and extend this.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
SKILL_DIR = EVAL_DIR.parent
FIXTURES_DIR = EVAL_DIR / "fixtures"
MODEL = os.environ.get("EVAL_MODEL", "claude-sonnet-4-5")
API_URL = "https://api.anthropic.com/v1/messages"

DIMENSIONS = [
    "seo_basics",
    "aeo_geo_content",
    "product_knowledge",
    "agent_access",
    "policy_support",
    "commerce_action_readiness",
]

VALID_ROUTES = {"Not Qualified", "Verified Audit", "Custom Agent", "Forward Deployed Engineering"}

FORBIDDEN_ANALYTICS_PATTERN = re.compile(
    r"(search console|google analytics|conversion rate|revenue|traffic (data|numbers)|ranking (position|data))",
    re.IGNORECASE,
)
VERIFIED_EXPORT_PATTERN = re.compile(r"verified export", re.IGNORECASE)
NEGATION_PATTERN = re.compile(
    r"\b(no|not|without|lacks?|lacking|none|unavailable|doesn't|does not|didn't|did not|"
    r"n/a|not provided|not observed|not available)\b",
    re.IGNORECASE,
)
SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")

RESPONSE_SCHEMA_INSTRUCTIONS = """
Respond with ONLY a single JSON object (no prose, no markdown fences) matching this shape:

{
  "dimensions": {
    "seo_basics": {"score": <0-3 integer>, "evidence": "<what you observed in the input and where>"},
    "aeo_geo_content": {"score": <0-3 integer>, "evidence": "..."},
    "product_knowledge": {"score": <0-3 integer>, "evidence": "..."},
    "agent_access": {"score": <0-3 integer>, "evidence": "..."},
    "policy_support": {"score": <0-3 integer>, "evidence": "..."},
    "commerce_action_readiness": {"score": <0-3 integer>, "evidence": "..."}
  },
  "routing": "<one of: Not Qualified, Verified Audit, Custom Agent, Forward Deployed Engineering>",
  "notes": "<any limitations, e.g. that this is a public-signal-only review>"
}

Score every dimension strictly from the HTML provided. Do not claim access to Search Console,
analytics, revenue, rankings, or conversion data -- none were provided.
"""


def load_skill_prompt() -> str:
    skill_md = (SKILL_DIR / "SKILL.md").read_text()
    example = (SKILL_DIR / "references" / "example-audit.md").read_text()
    return (
        skill_md
        + "\n\n## Worked example (for calibration only, do not reuse its scores)\n\n"
        + example
        + "\n\n"
        + RESPONSE_SCHEMA_INSTRUCTIONS
    )


def call_model(system_prompt: str, fixture_html: str, url: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    body = {
        "model": MODEL,
        "max_tokens": 1500,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Submitted URL: {url}\n\n"
                    "Public HTML snapshot fetched for this URL (treat as the only "
                    "available public signal; there is no robots.txt, sitemap, or "
                    "other fetch available beyond what is embedded below):\n\n"
                    f"{fixture_html}"
                ),
            }
        ],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read())
    return "".join(block.get("text", "") for block in payload.get("content", []))


def extract_json(raw_text: str) -> dict:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    return json.loads(text)


def check_result(result: dict, expected_routing: str, raw_text: str) -> list[str]:
    failures = []

    dims = result.get("dimensions")
    if not isinstance(dims, dict):
        failures.append("missing or malformed 'dimensions' object")
        dims = {}

    for dim in DIMENSIONS:
        entry = dims.get(dim)
        if not isinstance(entry, dict):
            failures.append(f"dimension '{dim}' missing")
            continue
        score = entry.get("score")
        if not isinstance(score, int) or not (0 <= score <= 3):
            failures.append(f"dimension '{dim}' score must be an integer 0-3, got {score!r}")
        evidence = entry.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            failures.append(f"dimension '{dim}' has no cited evidence")

    routing = result.get("routing")
    if not isinstance(routing, str) or routing not in VALID_ROUTES:
        failures.append(f"routing must be exactly one of {sorted(VALID_ROUTES)}, got {routing!r}")
    elif routing != expected_routing:
        failures.append(f"expected routing '{expected_routing}', got '{routing}'")

    unverified_claims = find_unverified_analytics_claims(raw_text)
    if unverified_claims:
        failures.append(
            "response claims analytics/Search Console/revenue/ranking data without citing a "
            f"verified export: {unverified_claims!r}"
        )

    return failures


def find_unverified_analytics_claims(raw_text: str) -> list[str]:
    """Return sentences that claim analytics-style access rather than disclaim it.

    A sentence mentioning revenue/rankings/traffic/analytics is only a guardrail
    violation if it asserts access to that data. The skill's own guardrails push
    the model to *disclaim* lacking that data (e.g. "no revenue data was
    observed"), so a sentence containing a negation word is treated as compliant
    unless it also cites a verified export.
    """
    claims = []
    for sentence in SENTENCE_SPLIT_PATTERN.split(raw_text):
        if not FORBIDDEN_ANALYTICS_PATTERN.search(sentence):
            continue
        if VERIFIED_EXPORT_PATTERN.search(sentence):
            continue
        if NEGATION_PATTERN.search(sentence):
            continue
        claims.append(sentence.strip())
    return claims


def run_fixture(fixture_path: Path, system_prompt: str) -> bool:
    expected_path = fixture_path.with_suffix("").with_suffix(".expected.json")
    expected = json.loads(expected_path.read_text())
    fixture_html = fixture_path.read_text()

    print(f"--- {fixture_path.name} ---")
    try:
        raw_text = call_model(system_prompt, fixture_html, expected["url"])
    except (urllib.error.URLError, RuntimeError) as exc:
        print(f"FAIL: could not call model: {exc}")
        return False

    try:
        result = extract_json(raw_text)
    except json.JSONDecodeError as exc:
        print(f"FAIL: response was not valid JSON ({exc})")
        print(raw_text)
        return False

    failures = check_result(result, expected["expected_routing"], raw_text)
    if failures:
        print("FAIL:")
        for failure in failures:
            print(f"  - {failure}")
        return False

    print(f"PASS: routed to '{result['routing']}' as expected")
    return True


def main() -> int:
    fixtures = sorted(FIXTURES_DIR.glob("*.html"))
    if not fixtures:
        print("No fixtures found under eval/fixtures/", file=sys.stderr)
        return 1

    system_prompt = load_skill_prompt()
    all_passed = True
    for fixture_path in fixtures:
        if not run_fixture(fixture_path, system_prompt):
            all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
