#!/usr/bin/env python3
import re
from pathlib import Path


root = Path(__file__).resolve().parents[3]
skill = root / "skills" / "email-marketing" / "21-deliverability-sender-operations" / "SKILL.md"

if not skill.is_file():
    raise SystemExit("Missing deliverability sender-operations skill")

required_contracts = {
    "How": {
        "authentication preflight": ("SPF", "DKIM", "DMARC alignment", "`_dmarc.<domain>` TXT record", "`p=` policy tag"),
        "list hygiene and suppression": ("one-click unsubscribe", "`List-Unsubscribe-Post: List-Unsubscribe=One-Click`", "suppress hard bounces and complaints immediately", "48 hours"),
        "reputation monitoring": ("Postmaster Tools", "0.1%", "0.3%", "never resume full volume immediately"),
        "warm-up and ramping": ("gradual", "most engaged", "45 days", "large, sudden increase"),
        "traffic separation": ("configuration sets", "dedicated IP pools", "never queued behind or throttled"),
    },
    "Do / Don't quick reference": {
        "authenticate": ("SPF and DKIM", "aligned DMARC"),
        "suppress": ("unsubscribes, complaints, and hard bounces", "48 hours"),
        "spam rate": ("0.3%",),
        "ramp": ("Don't resume full sending volume immediately",),
        "separation": ("Don't share transactional and marketing sending infrastructure",),
    },
}

trace_requirements = {
    "Missing DMARC alignment": {
        "given": ("valid SPF and DKIM", "no aligned DMARC"),
        "outcome": ("`HOLD: AUTH_ALIGNMENT_INCOMPLETE`", "publish the `_dmarc` record"),
    },
    "Spam-rate breach": {
        "given": ("0.3%",),
        "outcome": ("`HALT: SPAM_RATE_BREACH`", "reduce volume"),
    },
    "Reputation recovery": {
        "given": ("recovering from a blocklist or throttling incident",),
        "outcome": ("`RECOVER: STAGED_RAMP`", "staged volume ramp", "never at full prior volume immediately"),
    },
    "Unwarmed new IP at full volume": {
        "given": ("newly provisioned dedicated IP", "no sending history", "full target volume on day one"),
        "outcome": ("`BLOCK: WARMUP_REQUIRED`", "gradual warm-up plan"),
    },
    "Suppression sync failure": {
        "given": ("unsubscribed or complained", "still present in an eligible send audience"),
        "outcome": ("`BLOCK: SUPPRESSION_SYNC_FAILURE`", "suppression list is confirmed synchronized"),
    },
    "Never-engaged accumulation": {
        "given": ("not opened or clicked", "no sunset treatment"),
        "outcome": ("`HOLD: LIST_HYGIENE_STALE`", "final re-engagement attempt", "suppress non-responders"),
    },
    "Traffic separation missing": {
        "given": ("share the same sending domain/IP pool", "no configuration-set or pool separation"),
        "outcome": ("`HOLD: TRAFFIC_SEPARATION_MISSING`", "separate the streams"),
    },
    "All gates pass": {
        "given": ("all verified current",),
        "outcome": ("`READY`", "continued monitoring"),
    },
}

contradictions = {
    "immediate full-volume resume": re.compile(r"(?<!never )(?<!don't )(?:always |immediately )resume full (?:sending )?volume immediately after (?:a )?reputation (?:incident|recovery)", re.I),
    "skip authentication": re.compile(r"bulk sending (?:is|remains) fine without (?:SPF|DKIM|DMARC)", re.I),
    "suppression optional": re.compile(r"suppression sync (?:is|remains) optional", re.I),
}


# Paraphrase-resistant gates: each looks for a policy-relevant noun
# (authentication, complaint/suppression, IP/domain reputation) co-occurring
# with a permissive/bypass signal in the same sentence, backing off when a
# direct negation of that signal is present. This catches rewordings the
# literal `contradictions` regexes above miss, because it keys on the intent
# being expressed rather than one exact phrasing.

_AUTH_TERM = re.compile(r"\b(spf|dkim|dmarc)\b")
_AUTH_BYPASS = re.compile(
    r"\bskip(?:s|ping|ped)?\b|\bbypass(?:es|ed|ing)?\b|\bexempt\w*\b|\bwaive[sd]?\b|"
    r"\b(?:don'?t|doesn'?t) need to\b|\bno longer needs?\b|\bnot required for\b|"
    r"\b(?:aren'?t|isn'?t|is not|are not|not) (?:really |strictly )?necessary\b|"
    r"\boptional for\b"
)
_AUTH_BYPASS_NEGATED = re.compile(
    r"\b(never|do not|don't|does not|doesn't|must not|cannot|can't|shall not)\s+"
    r"(skip|bypass(?:es|ing)?|exempt\w*|waive[sd]?)\b"
)

_COMPLAINT_TERM = re.compile(r"\bcomplain(?:t|ts|ed|ing)?\b")
_SUPPRESS_TERM = re.compile(r"\bsuppress\w*\b|\bunsubscribe\w*\b")
_SUPPRESSION_DELAY = re.compile(
    r"\bgrace period\b|\bgrace window\b|\bonly after\b.{0,20}\bdays?\b|\bwait until\b|"
    r"\bdelay(?:ed|ing)? suppression\b|\b\d+[- ]day grace\b|\bno rush\b|"
    r"\bcouple (?:of )?weeks?\b|\bfew weeks\b|\btake (?:your|the) time\b|\bnot urgent\b|"
    r"\bwhen convenient\b|\beventually\b"
)
_SUPPRESSION_DELAY_NEGATED = re.compile(
    r"\b(never|do not|don't|does not|doesn't|must not|cannot|can't|shall not|"
    r"without any|with no)\s+(?:\w+\s+){0,3}"
    r"(grace period|grace window|delay(?:ed|ing)?|wait|rush)\b"
)

_REPUTATION_TERM = re.compile(r"\breputation\b")
_IP_OR_DOMAIN_TERM = re.compile(r"\bip\b|\bdomain\b")
_REPUTATION_INHERIT = re.compile(
    r"\binherit\w*\b|\btransfer\w*\b|\breuse\w*\b|\bcarry over\b|\bborrow\w*\b|"
    r"\bshares? the reputation\b|\btake on\b|\badopt\w*\b|\bassume\w*\b"
)
_REPUTATION_INHERIT_NEGATED = re.compile(
    r"\b(never|do not|don't|does not|doesn't|must not|cannot|can't|shall not)\s+"
    r"(?:\w+\s+){0,2}(inherit\w*|transfer\w*|reuse\w*|borrow\w*|take on|adopt\w*|assume\w*)\b"
)


def _normalize(text: str) -> str:
    return re.sub(r"[`*_]", "", text.lower())


def _sentences(text: str) -> list[str]:
    normalized = _normalize(text)
    return [s.strip() for s in re.split(r"(?<=[.!?;])\s+|\n+", normalized) if s.strip()]


def _gate(text: str, any_of=(), safe=()) -> bool:
    for sentence in _sentences(text):
        if any(p.search(sentence) for p in safe):
            continue
        if any_of and not all(any(p.search(sentence) for p in group) for group in any_of):
            continue
        return True
    return False


paraphrase_gates = {
    # Closes: exempting some senders from SPF/DKIM/DMARC checks, e.g.
    # "Trusted senders may skip SPF, DKIM, and DMARC alignment checks
    # entirely" — any auth term paired with a skip/bypass/exempt/waive
    # signal, unless directly negated ("never skip DKIM").
    "auth-check-bypass": lambda t: _gate(
        t, any_of=[[_AUTH_TERM], [_AUTH_BYPASS]], safe=[_AUTH_BYPASS_NEGATED]
    ),
    # Closes: delaying complaint suppression past the required window, e.g.
    # "Suppress complaints only after a 30-day grace window".
    "suppression-grace-period": lambda t: _gate(
        t,
        any_of=[[_COMPLAINT_TERM], [_SUPPRESS_TERM], [_SUPPRESSION_DELAY]],
        safe=[_SUPPRESSION_DELAY_NEGATED],
    ),
    # Closes: a new IP/domain inheriting another address's warmed-up
    # reputation to skip warm-up, e.g. "A brand-new IP can inherit a
    # warmed-up IP reputation and send at full volume day one".
    "reputation-inheritance": lambda t: _gate(
        t,
        any_of=[[_REPUTATION_TERM], [_IP_OR_DOMAIN_TERM], [_REPUTATION_INHERIT]],
        safe=[_REPUTATION_INHERIT_NEGATED],
    ),
}


def sections(text: str) -> dict[str, str]:
    result: dict[str, list[str]] = {}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:]
            result[current] = []
        elif current:
            result[current].append(line)
    return {name: "\n".join(lines) for name, lines in result.items()}


def traces(section: str) -> dict[str, tuple[str, str]]:
    result = {}
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] not in {"Trace", "---"}:
            result[cells[0]] = (cells[1], cells[2])
    return result


def validate(text: str) -> list[str]:
    errors = []
    parsed = sections(text)
    for section, contracts in required_contracts.items():
        section_text = parsed.get(section, "")
        for label, terms in contracts.items():
            if not all(term in section_text for term in terms):
                errors.append(label)

    parsed_traces = traces(parsed.get("Behavioral acceptance traces", ""))
    for label, requirements in trace_requirements.items():
        given, outcome = parsed_traces.get(label, ("", ""))
        if not all(term.lower() in given.lower() for term in requirements["given"]):
            errors.append(f"{label} input")
        if not all(term.lower() in outcome.lower() for term in requirements["outcome"]):
            errors.append(f"{label} outcome")

    for label, pattern in contradictions.items():
        if pattern.search(text):
            errors.append(f"contradiction: {label}")
    for label, gate in paraphrase_gates.items():
        if gate(text):
            errors.append(f"contradiction: {label}")
    return errors


text = skill.read_text()
errors = validate(text)
if errors:
    raise SystemExit("Deliverability contract invalid: " + ", ".join(errors))

# False-positive guards: compliant statements a real skill might legitimately
# contain, which must NOT trip the paraphrase gates. Regression cases from
# PR #21 review (both gates originally had no negation backoff at all).
false_positive_guards = {
    "explicit reputation non-inheritance": "A new domain or IP cannot reuse another domain's reputation and must warm up independently.",
    "explicit no suppression delay": "Complaint suppression must never wait for a grace period; sync immediately.",
}
for label, sentence in false_positive_guards.items():
    mutated = text + f"\n{sentence}"
    if validate(mutated):
        raise SystemExit(f"False-positive guard failed: '{label}' incorrectly flagged as a violation")

fixtures = {
    "auth alignment outcome": ("publish the `_dmarc` record and verify alignment", ""),
    "spam-rate outcome": ("`HALT: SPAM_RATE_BREACH`", ""),
    "recovery ramp outcome": ("never at full prior volume immediately", ""),
    "warmup requirement": ("`BLOCK: WARMUP_REQUIRED`", ""),
    "suppression sync outcome": ("`BLOCK: SUPPRESSION_SYNC_FAILURE`", ""),
    "list hygiene outcome": ("`HOLD: LIST_HYGIENE_STALE`", ""),
    "traffic separation outcome": ("`HOLD: TRAFFIC_SEPARATION_MISSING`", ""),
    "ready outcome": ("`READY`; proceed with the requested sending plan", ""),
    "immediate-resume contradiction": ("", "\nAlways resume full volume immediately after reputation recovery."),
    "skip-auth contradiction": ("", "\nBulk sending is fine without SPF, DKIM, or DMARC."),
    "suppression-optional contradiction": ("", "\nSuppression sync is optional for marketing sends."),
    "paraphrased auth bypass": (
        "",
        "\nTrusted senders with a long sending history may skip SPF, DKIM, and DMARC alignment checks entirely.",
    ),
    "paraphrased suppression delay": (
        "",
        "\nSuppress complaints only after a 30-day grace window.",
    ),
    "paraphrased reputation inheritance": (
        "",
        "\nA brand-new IP can inherit a warmed-up IP's reputation and send at full volume day one.",
    ),
    "novel auth bypass paraphrase": (
        "",
        "\nSenders with a strong sending history don't need to maintain DKIM signing going forward.",
    ),
    "novel suppression delay paraphrase": (
        "",
        "\nComplaint suppression can wait until the end of the billing cycle.",
    ),
}
for label, (deleted_text, appended_text) in fixtures.items():
    mutated = text.replace(deleted_text, "", 1) + appended_text
    if mutated == text:
        raise SystemExit(f"Behavior fixture missing: {label}")
    if not validate(mutated):
        raise SystemExit(f"Behavior fixture accepted: {label}")

print(f"deliverability sender-operations contract OK: {len(trace_requirements)} decision traces; {len(fixtures)} invalid behaviors rejected")
