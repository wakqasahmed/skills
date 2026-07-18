#!/usr/bin/env python3
"""Offline contract checks for the commerce-protocol-readiness behavior eval.

This is deliberately not an agent evaluator. It verifies the checked-in
SKILL.md contract and held-out case manifest only; model outcomes are produced
and scored by the explicitly gated harness documented in eval/README.md.
"""
import json
import re
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
SKILL_MD = EVAL_DIR.parent / "SKILL.md"
CASES_PATH = EVAL_DIR / "held-out-cases.json"
SHARED_GUARDRAILS = EVAL_DIR.parent.parent / "references" / "guardrails.md"
REQUIRED_SKILL_TERMS = (
    "Classify the commerce goal",
    "Score each protocol as",
    "Recommend the smallest next implementation",
    "../references/guardrails.md",
)
REQUIRED_CASE_FIELDS = {
    "id",
    "split",
    "prompt",
    "expected_skill_usage",
    "expected_outcome",
    "expected_safety_outcome",
}
REQUIRED_SAFETY_TERMS = (
    "identity verification",
    "consent capture",
    "audit logging",
    "fraud controls",
    "human escalation path",
)
PROHIBITION_CUES = ("do not", "does not", "must not", "should not", "never", "shall not")
PERMISSIVE_RED_FLAGS = (
    "nice-to-have", "nice to have", "optional", "can strengthen", "over time",
    "where practical", "prefer to", "preferably", "if possible", "when convenient",
    "at least one",
)


def sentences_mentioning(text: str, phrase: str) -> list[str]:
    return [" ".join(sentence.split()) for sentence in re.split(r"(?<=[.!?])\s+", text) if phrase in sentence]


def check_guardrail_text_in(skill_md: str, shared_guardrails_md: str) -> list[str]:
    if "## Guardrails" not in skill_md:
        return ["SKILL.md has no '## Guardrails' section"]
    if "../references/guardrails.md" not in skill_md.split("## Guardrails", 1)[1]:
        return ["SKILL.md no longer links to the shared guardrails contract"]
    if "## Autonomous action safety" not in shared_guardrails_md:
        return ["shared guardrails has no '## Autonomous action safety' section"]

    section = shared_guardrails_md.split("## Autonomous action safety", 1)[1].lower()
    failures = []
    for term in REQUIRED_SAFETY_TERMS:
        if term not in section:
            failures.append(f"shared guardrails are missing required safety text: {term}")

    action_sentences = sentences_mentioning(section, "autonomous checkout")
    payment_sentences = [sentence for sentence in sentences_mentioning(section, "autonomous") if "payment" in sentence]
    if not any(cue in sentence and "recommend" in sentence for sentence in action_sentences for cue in PROHIBITION_CUES):
        failures.append("autonomous actions lack hard prohibition framing")
    without_sentences = [sentence for sentence in action_sentences if "without" in sentence]
    if not without_sentences:
        failures.append("autonomous actions do not make safeguards a precondition")
    elif any(" or " in sentence.partition("without")[2] for sentence in without_sentences):
        failures.append("required autonomous-payment safeguards are joined with 'or'")
    for sentence in action_sentences + payment_sentences:
        for red_flag in PERMISSIVE_RED_FLAGS:
            if red_flag in sentence:
                failures.append(f"autonomous-payment guardrail contains permissive language: {red_flag}")
    if not any(
        "before it is recommended" in sentence
        and all(term in sentence for term in ("identity verification", "consent capture", "fraud controls"))
        for sentence in payment_sentences
    ):
        failures.append("autonomous payment does not require identity, consent, and fraud controls")
    return failures


def validate_static_safety_contract() -> list[str]:
    return check_guardrail_text_in(SKILL_MD.read_text(), SHARED_GUARDRAILS.read_text())


def validate_contract() -> list[str]:
    failures = []
    skill_text = SKILL_MD.read_text()
    for term in REQUIRED_SKILL_TERMS:
        if term not in skill_text:
            failures.append(f"SKILL.md is missing required contract text: {term}")

    failures.extend(validate_static_safety_contract())

    cases = json.loads(CASES_PATH.read_text()).get("cases", [])
    if len(cases) < 10:
        failures.append("held-out manifest must contain at least 10 cases")

    identifiers = set()
    usage_counts = {"use": 0, "do_not_use": 0}
    for case in cases:
        missing = REQUIRED_CASE_FIELDS - case.keys()
        if missing:
            failures.append(f"{case.get('id', '<unknown>')} is missing {sorted(missing)}")
            continue
        if case["id"] in identifiers:
            failures.append(f"duplicate case id: {case['id']}")
        identifiers.add(case["id"])
        if case["split"] != "held_out":
            failures.append(f"{case['id']} is not held out")
        if case["expected_skill_usage"] not in usage_counts:
            failures.append(f"{case['id']} has invalid skill-usage expectation")
        else:
            usage_counts[case["expected_skill_usage"]] += 1
        if not case["expected_safety_outcome"].strip():
            failures.append(f"{case['id']} has no explicit safety outcome")

    for usage, count in usage_counts.items():
        if count < 5:
            failures.append(f"held-out manifest needs at least 5 {usage} cases")
    return failures


def main() -> int:
    failures = validate_contract()
    if failures:
        print("FAIL: deterministic contract checks")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: deterministic contract checks")
    print("Harness gate: run the credentialed, isolated ablation described in eval/README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
