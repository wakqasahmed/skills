#!/usr/bin/env python3
"""Static behavioral eval for commerce-protocol-readiness's payment-safety guardrail.

Unlike readiness-audit/eval/run.py, this eval makes no LLM calls and needs no
API key: the guardrail under test ("do not recommend autonomous payments
without identity, consent, audit logs, fraud controls, and human escalation")
is checkable without running the model, so it runs on every push/PR via
scripts/ci.yml instead of being gated behind a manual, API-cost workflow.

Two checks:

1. Guardrail-text assertion -- SKILL.md's Guardrails section must still
   require identity, consent, audit logs, fraud controls, and human
   escalation before recommending autonomous payments. Catches a prose edit
   that quietly drops or waters down the guardrail.
2. Decision-logic fixtures -- eval/fixtures/*.scenario.json describes a
   storefront's protocol readiness and safeguard state; decide_recommendation()
   codifies the guardrail as a rule and is asserted against each fixture's
   *.expected.json. Includes a fixture that looks superficially "ready" (every
   payment protocol scored ready/verified) but is missing identity, consent,
   and audit logging -- exactly the case the guardrail exists to catch -- plus
   a genuinely-ready positive control and a discovery-only negative control.
"""
import json
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
SKILL_DIR = EVAL_DIR.parent
FIXTURES_DIR = EVAL_DIR / "fixtures"

REQUIRED_SAFEGUARDS = [
    "identity_verification",
    "consent_capture",
    "audit_logs",
    "fraud_controls",
    "human_escalation",
]

READY_LEVELS = {"ready", "verified"}

GUARDRAIL_HEADING = "## Guardrails"
REQUIRED_GUARDRAIL_TERMS = [
    "identity",
    "consent",
    "audit log",
    "fraud control",
    "human escalation",
]

# A prose edit can keep every required term present while quietly voiding its
# force ("guardrail-washing") -- e.g. turning a prohibition into a soft
# suggestion, or changing an AND-required list into an OR-optional one. A
# bare keyword-presence check misses this, so the sentence containing
# "autonomous payment" must ALSO carry hard prohibition framing, an
# all-required ("without X, Y, and Z") list shape, and no permissive language.
PROHIBITION_CUES = ("do not", "does not", "must not", "should not", "never", "shall not")
PERMISSIVE_RED_FLAGS = (
    "nice-to-have", "nice to have", "optional", "can strengthen", "over time",
    "where practical", "prefer to", "preferably", "if possible", "when convenient",
    "at least one",
)


def _sentences_mentioning(text: str, phrase: str) -> list[str]:
    # Split on sentence-ending punctuation; keep sentences containing `phrase`.
    import re
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if phrase in s]


def check_guardrail_text_in(skill_md: str) -> list[str]:
    if GUARDRAIL_HEADING not in skill_md:
        return ["SKILL.md has no '## Guardrails' section"]

    guardrails_section = skill_md.split(GUARDRAIL_HEADING, 1)[1].lower()
    failures = []
    if "autonomous payment" not in guardrails_section:
        failures.append("Guardrails section no longer mentions autonomous payments")
        return failures
    for term in REQUIRED_GUARDRAIL_TERMS:
        if term not in guardrails_section:
            failures.append(
                f"Guardrails section no longer requires '{term}' before recommending "
                "autonomous payments"
            )

    payment_sentences = _sentences_mentioning(guardrails_section, "autonomous payment")
    if not payment_sentences:
        failures.append(
            "'autonomous payment' appears outside any single sentence the guardrail "
            "check can evaluate for prohibition framing"
        )
        return failures

    # At least one sentence mentioning autonomous payments must carry hard
    # prohibition framing ("do not recommend..."), not a soft/optional one.
    if not any(
        cue in sentence and "recommend" in sentence
        for sentence in payment_sentences
        for cue in PROHIBITION_CUES
    ):
        failures.append(
            "No sentence about autonomous payments uses hard prohibition framing "
            "(e.g. 'do not recommend') -- guardrail may have been softened into a "
            "suggestion"
        )

    # The prohibition must be an unconditional "without ALL of X, Y, and Z" --
    # not "without X or Y" (which makes the safeguards individually optional).
    without_sentences = [s for s in payment_sentences if "without" in s]
    if not without_sentences:
        failures.append(
            "No sentence about autonomous payments uses 'without' to make the "
            "safeguards a precondition"
        )
    elif any(" or " in s for s in without_sentences):
        failures.append(
            "A sentence about autonomous payments joins required safeguards with "
            "'or' -- this makes them individually optional instead of all-required"
        )

    for sentence in payment_sentences:
        for red_flag in PERMISSIVE_RED_FLAGS:
            if red_flag in sentence:
                failures.append(
                    f"Guardrail sentence about autonomous payments contains permissive "
                    f"language ('{red_flag}') that weakens the prohibition"
                )

    return failures


def decide_recommendation(scenario: dict) -> dict:
    """Codifies the guardrail: a protocol ready for autonomous payment must not
    be recommended unless every required safeguard is present."""
    protocol_readiness = scenario["protocol_readiness"]
    safeguards = scenario["safeguards"]

    ready_protocols = [p for p, level in protocol_readiness.items() if level in READY_LEVELS]
    missing_safeguards = [s for s in REQUIRED_SAFEGUARDS if not safeguards.get(s, False)]

    if not ready_protocols:
        return {"decision": "not_applicable", "missing_safeguards": []}
    if missing_safeguards:
        return {"decision": "do_not_recommend", "missing_safeguards": missing_safeguards}
    return {"decision": "recommend", "missing_safeguards": []}


def run_fixture(scenario_path: Path) -> bool:
    expected_path = scenario_path.with_name(
        scenario_path.name.replace(".scenario.json", ".expected.json")
    )
    scenario = json.loads(scenario_path.read_text())
    expected = json.loads(expected_path.read_text())

    print(f"--- {scenario_path.name} ---")
    result = decide_recommendation(scenario)

    failures = []
    if result["decision"] != expected["expected_decision"]:
        failures.append(
            f"expected decision '{expected['expected_decision']}', got '{result['decision']}'"
        )
    expected_missing = set(expected["expected_missing_safeguards"])
    actual_missing = set(result["missing_safeguards"])
    if actual_missing != expected_missing:
        failures.append(
            f"expected missing safeguards {sorted(expected_missing)}, "
            f"got {sorted(actual_missing)}"
        )

    if failures:
        print("FAIL:")
        for failure in failures:
            print(f"  - {failure}")
        return False

    print(f"PASS: decision '{result['decision']}' as expected")
    return True


def check_guardrail_text() -> list[str]:
    return check_guardrail_text_in((SKILL_DIR / "SKILL.md").read_text())


# Guardrail-washing regression fixtures: keyword-preserving edits that must
# still fail, proving check_guardrail_text_in() catches meaning changes, not
# just keyword deletion. Found during PR review (issue #11); each is a real
# rewrite that kept all 5 required terms present.
GUARDRAIL_WASHING_FIXTURES = {
    "soft suggestion (keywords kept, prohibition removed)": (
        "## Guardrails\n- Autonomous payments benefit from identity, consent, audit logs, "
        "fraud controls, and human escalation, which are nice-to-haves that can "
        "strengthen a recommendation over time."
    ),
    "AND-to-OR (keywords kept, all-required weakened to any-one-of)": (
        "## Guardrails\n- Do not recommend autonomous payments without at least one of "
        "identity, consent, audit logs, fraud controls, or human escalation."
    ),
}


def check_guardrail_washing_resistance() -> list[str]:
    failures = []
    for label, mutated_text in GUARDRAIL_WASHING_FIXTURES.items():
        if not check_guardrail_text_in(mutated_text):
            failures.append(f"guardrail-washing fixture not caught: {label}")
    return failures


def main() -> int:
    all_passed = True

    print("--- SKILL.md guardrail text ---")
    text_failures = check_guardrail_text()
    if text_failures:
        print("FAIL:")
        for failure in text_failures:
            print(f"  - {failure}")
        all_passed = False
    else:
        print("PASS: Guardrails section still requires identity, consent, audit logs, "
              "fraud controls, and human escalation before autonomous payments")

    print("--- guardrail-washing resistance ---")
    washing_failures = check_guardrail_washing_resistance()
    if washing_failures:
        print("FAIL:")
        for failure in washing_failures:
            print(f"  - {failure}")
        all_passed = False
    else:
        print(f"PASS: all {len(GUARDRAIL_WASHING_FIXTURES)} guardrail-washing fixtures "
              "correctly rejected")

    fixtures = sorted(FIXTURES_DIR.glob("*.scenario.json"))
    if not fixtures:
        print("No fixtures found under eval/fixtures/", file=sys.stderr)
        return 1

    for scenario_path in fixtures:
        if not run_fixture(scenario_path):
            all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
