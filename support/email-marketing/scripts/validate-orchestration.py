#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[3]
skill = root / "skills" / "email-marketing" / "19-lifecycle-orchestration" / "SKILL.md"

if not skill.is_file():
    raise SystemExit("Missing lifecycle orchestration skill")

required_lines = {
    "Contact-level decision order": {
        "contact-level decision": "Evaluate each contact at reservation time and again immediately before send, recording the input snapshot, winning candidate, rejected candidates, reason codes, next eligible time, and policy version. [HUB-WF-01][BRAZE-STRAT-01]",
        "classify before permissions": "1. Classify every candidate by primary purpose as essential service, marketing, or mixed; treat mixed messages as marketing and never relabel a promotion to win priority. [BRAZE-TRANS-01][FTC-01]",
        "class-specific suppression": "3. Apply legal basis, consent, unsubscribe, complaint, and purpose/channel suppression gates to marketing and mixed candidates; block the affected marketing candidate without blocking a separately verified essential-service candidate. [ICO-02][GMAIL-01][BRAZE-TRANS-01]",
        "service priority": "7. When event-bound service information is verified, essential service messages bypass marketing scheduling, quiet periods, and marketing caps; they must never carry marketing content or reset, evade, or consume marketing caps. [BRAZE-TRANS-01][FTC-01]",
    },
    "Event precedence and ownership": {
        "atomic ownership": "- Acquire one owning flow with an atomic compare-and-set or transaction keyed by contact, objective, and subject entity, and persist its entry event, entry time, current step, exit conditions, and ownership expiry; exactly one concurrent worker proceeds and each loser records `DROP: OWNERSHIP_CONFLICT`. [HUB-WF-01][BRAZE-TRIG-01]",
        "business-owned precedence": "- Resolve remaining marketing conflicts only with a published, business-owned precedence table based on current intent and message expiry, not whichever automation runs first; return `HOLD: PRECEDENCE_POLICY_MISSING` when no applicable table exists. [BRAZE-TRIG-01][BRAZE-STRAT-01]",
    },
    "Pressure, suppression, and experiments": {
        "exclusive winner reservation": "- In one atomic transaction, validate and reserve ownership and canonical deduplication, count and reserve every applicable global and segment pressure window, and write one exclusive winner slot keyed by contact and decision window; an exhausted cap returns `DEFER: CAP_REACHED`, otherwise a candidate finding that winner slot returns `DEFER: DECISION_WINDOW_TAKEN`, and every failed transaction rolls back all reservations. [HUB-WF-01][BRAZE-TRIG-01][BRAZE-STRAT-01][BRAZE-HOLIDAY-01]",
        "channel preferences": "- Apply the recipient's permitted channels and stated topic/frequency choices first, choose only an allowed channel, and do not substitute email, SMS, push, or another channel without permission for that channel and purpose. [ICO-02][BRAZE-STRAT-01]",
        "quiet periods": "- Defer non-urgent marketing to the first eligible local time after the quiet period only if the trigger remains valid; when timezone is unknown, use the documented conservative fallback or return `HOLD`. [BRAZE-STRAT-01][HUB-WF-01]",
        "semantic-slot deduplication": "- Build the versioned canonical deduplication key as `v2|contact_id|purpose|event_type|event_id|entity_type|entity_id|message_slot`, using normalized authoritative event and entity IDs together and the literal `none` only when a field is not applicable; define `message_slot` as a business-owned semantic identity such as `cart-reminder-1`, never a provider flow, step, template, or channel ID, so equivalent messages collide across implementations and channels while a legitimate later sequence slot remains distinct; atomically reserve the key in the winner transaction and return `DROP: DUPLICATE` for a matching reservation or send in its validity window. [BRAZE-TRIG-01][HUB-WF-01]",
        "recent-purchase suppression": "- Define recent-purchase suppression by product/category, campaign purpose, and a documented lookback window; suppress stale acquisition, browse, cart, price, or incompatible recommendation messages while preserving relevant service and post-purchase information. [KL-BROWSE-01][KL-LOWSTOCK-01][KL-XSELL-01][BRAZE-TRANS-01]",
        "durable holdout": "- Before a coordinated experiment starts, persist its experiment ID, contact randomization unit, sampled control membership, variant, eligibility snapshot, named campaign/flow scope, and start/end; keep that assignment unchanged through the test, exclude control members from every marketing treatment in scope across channels, and preserve essential-service eligibility. [KL-HOLDOUT-01][BRAZE-TRANS-01]",
    },
    "Behavioral acceptance traces": {
        "marketing opt-out service trace": "| Marketing opt-out with verified receipt | Marketing candidate is unsubscribed; a separately verified order receipt is eligible. | `BLOCK: UNSUBSCRIBED` for marketing and `SEND` for the receipt; the marketing block does not block essential service. [ICO-02][BRAZE-TRANS-01] |",
        "ownership collision trace": "| Concurrent ownership | Two workers request the same contact, objective, and entity with no existing owner. | One atomic acquisition wins; exactly one worker proceeds and the loser records `DROP: OWNERSHIP_CONFLICT`. [HUB-WF-01][BRAZE-TRIG-01] |",
        "cap boundary trace": "| Concurrent cap boundary | Two distinct candidates and deduplication keys observe one remaining pressure slot. | One atomic transaction selects one winner; the other records `DEFER: CAP_REACHED`, so reserved plus sent never exceeds the cap. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01] |",
        "decision-window headroom trace": "| Concurrent decision window with cap headroom | With cap 5 and pressure 0, two workers submit distinct eligible objectives, events, entities, and deduplication keys for the same contact and decision window. | One transaction writes the exclusive winner slot; the other records `DEFER: DECISION_WINDOW_TAKEN` even though four cap slots remain. [HUB-WF-01][BRAZE-STRAT-01] |",
        "cross-flow dedupe trace": "| Cross-flow and cross-channel duplicate | Different flows or channels produce the same semantic `message_slot` for the same contact, purpose, authoritative event, and entity. | All derive the same canonical key; one reservation wins and every other candidate records `DROP: DUPLICATE`. [BRAZE-TRIG-01][HUB-WF-01] |",
        "legitimate next-step trace": "| Legitimate next sequence step | `cart-reminder-1` was sent and the same contact, purpose, event, and entity later qualify for documented `cart-reminder-2`. | The semantic `message_slot` produces a distinct canonical key, so deduplication leaves step 2 eligible for the remaining policy gates. [BRAZE-TRIG-01][HUB-WF-01] |",
        "purchase suppression trace": "| Purchase after cart | A purchase event arrives after a cart candidate for the same order or cart. | State updates first and the cart candidate records `DROP: RECENT_PURCHASE`; relevant receipt or post-purchase service remains eligible. [KL-CART-01][KL-BROWSE-01][BRAZE-TRANS-01] |",
        "holdout leakage trace": "| Control leakage and service exception | A stored control member qualifies for two covered marketing flows and a verified receipt during the test window. | Both marketing candidates record `DROP: HOLDOUT`; the receipt remains eligible and no channel change bypasses the holdout. [KL-HOLDOUT-01][BRAZE-TRANS-01] |",
        "service-label abuse trace": "| Service-label abuse | Promotional content is labeled transactional or urgent. | Primary-purpose classification makes it marketing or mixed and `BLOCK`s any attempt to bypass consent, caps, deduplication, or holdout rules. [BRAZE-TRANS-01][FTC-01] |",
        "missing precedence trace": "| Missing precedence policy | Two otherwise eligible marketing candidates conflict and no applicable business-owned precedence table exists. | Policy readiness is `HOLD: PRECEDENCE_POLICY_MISSING`; neither candidate is selected by an invented default. [BRAZE-TRIG-01][BRAZE-STRAT-01] |",
    },
    "Mandatory output": {
        "campaign calendar": "4. Campaign calendar: date/time and timezone, campaign/flow, segment, channel, expected eligible volume, cap budget, holdout, owner, dependencies, and collision notes. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]",
        "monitoring": "5. Monitoring and exception report: sends/reservations by contact and flow, cap and quiet-period blocks, collisions won/lost, duplicate attempts, stale-event drops, purchase suppressions, holdout leakage, service latency, delivery/bounce/complaint metrics, and alerts with owners. [AWS-SES-MON-01][GMAIL-03][BRAZE-METRIC-01]",
    },
    "Agent restrictions": {
        "service anti-bypass": "- Never use an essential-service label, transactional stream, or urgent priority to carry promotion or bypass marketing consent, suppression, preferences, caps, quiet periods, deduplication, or holdouts. [BRAZE-TRANS-01][FTC-01]",
        "service experiment exclusion": "- Never withhold, delay behind marketing, or include essential service messages in marketing experiments or cap counts; monitor their latency and delivery separately. [BRAZE-TRANS-01][AWS-SES-SEP-01][AWS-SES-MON-01]",
    },
}


def sections(text: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:]
            result[current] = set()
        elif current and line:
            result[current].add(line)
    return result


def validate(text: str) -> list[str]:
    parsed = sections(text)
    missing = []
    for section, contracts in required_lines.items():
        section_lines = parsed.get(section, set())
        missing.extend(
            label for label, required_line in contracts.items() if required_line not in section_lines
        )
    return missing


text = skill.read_text()
missing = validate(text)
if missing:
    raise SystemExit("Lifecycle orchestration contract missing: " + ", ".join(missing))

mutations = {
    "class-specific suppression": "without blocking a separately verified essential-service candidate",
    "atomic ownership": "atomic compare-and-set or transaction",
    "business-owned precedence": "return `HOLD: PRECEDENCE_POLICY_MISSING`",
    "exclusive winner reservation": "write one exclusive winner slot keyed by contact and decision window",
    "semantic-slot deduplication": "business-owned semantic identity",
    "recent-purchase suppression": "suppress stale acquisition, browse, cart, price, or incompatible recommendation messages",
    "durable holdout": "keep that assignment unchanged through the test",
    "marketing opt-out service trace": "the marketing block does not block essential service",
    "ownership collision trace": "the loser records `DROP: OWNERSHIP_CONFLICT`",
    "cap boundary trace": "the other records `DEFER: CAP_REACHED`",
    "decision-window headroom trace": "even though four cap slots remain",
    "cross-flow dedupe trace": "every other candidate records `DROP: DUPLICATE`",
    "legitimate next-step trace": "deduplication leaves step 2 eligible",
    "purchase suppression trace": "the cart candidate records `DROP: RECENT_PURCHASE`",
    "holdout leakage trace": "no channel change bypasses the holdout",
    "service-label abuse trace": "any attempt to bypass consent, caps, deduplication, or holdout rules",
    "service anti-bypass": "or bypass marketing consent, suppression, preferences, caps, quiet periods, deduplication, or holdouts",
    "service experiment exclusion": "include essential service messages in marketing experiments or cap counts",
}
for expected_failure, deleted_text in mutations.items():
    mutated = text.replace(deleted_text, "", 1)
    if mutated == text:
        raise SystemExit(f"Mutation fixture missing: {expected_failure}")
    if expected_failure not in validate(mutated):
        raise SystemExit(f"Mutation check failed: deleting {expected_failure} was accepted")

print(f"lifecycle orchestration contract OK: {len(mutations)} mutations rejected")
