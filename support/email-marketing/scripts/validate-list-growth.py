#!/usr/bin/env python3
import re
from pathlib import Path


root = Path(__file__).resolve().parents[3]
skill = root / "skills" / "email-marketing" / "20-list-growth-signup-preferences" / "SKILL.md"

if not skill.is_file():
    raise SystemExit("Missing list-growth signup-preferences skill")

required_contracts = {
    "Consent-capture contract": {
        "guardrails and routing": ("00-email-marketing-guardrails", "18-jurisdiction-compliance-routing", "`HOLD`", "`BLOCK`"),
        "complete record": ("exact consent statement", "form version", "channel", "purpose", "confirmation state"),
        "expectations": ("sender", "channel", "purpose", "frequency", "separate unbundled choices"),
        "address verification": ("confirmation or double opt-in", "address ownership", "unconfirmed grant", "subscribed"),
    },
    "Double opt-in and welcome handoff": {
        "conditional use": ("single or double opt-in", "jurisdiction", "risk", "not a universal legal requirement"),
        "scoped pending state": ("`PENDING_CONFIRMATION`", "list, channel, and purpose", "only the confirmation message for that pending grant", "unrelated eligible service"),
        "scoped welcome handoff": ("`SUBSCRIBED`", "same list, channel, and purpose", "`02-welcome-onboarding`", "matching `PENDING_CONFIRMATION`"),
    },
    "Preferences and lead magnets": {
        "preferences": ("topic, channel, and frequency", "unsubscribe-all", "prior audit trail"),
        "lead magnet": ("resource", "marketing subscription separately", "without presenting access as proof of consent"),
        "prohibited acquisition": ("bought", "rented", "scraped", "harvested", "publicly copied"),
    },
}

trace_requirements = {
    "Incomplete consent record": {
        "given": ("lacks", "statement version", "channel"),
        "outcome": ("`HOLD: CONSENT_RECORD_INCOMPLETE`", "do not mark"),
    },
    "Double opt-in pending": {
        "given": ("list, email channel, and product-news purpose", "confirmation has not occurred"),
        "outcome": ("`PENDING_CONFIRMATION`", "confirmation message", "matching marketing and welcome"),
    },
    "Cross-purpose confirmation isolation": {
        "given": ("pending", "new product-news list", "existing education permission", "order receipt"),
        "outcome": ("new grant remains pending", "education permission and receipt remain eligible", "does not grant product-news marketing"),
    },
    "Preference change": {
        "given": ("weekly product news", "monthly education only"),
        "outcome": ("retain the prior record", "exclude weekly product news"),
    },
    "Lead magnet": {
        "given": ("guide", "separately offers", "email marketing"),
        "outcome": ("Deliver the guide", "subscribe only when", "no hidden or bundled permission"),
    },
    "Prohibited acquisition": {
        "given": ("bought or scraped", "marketing audience"),
        "outcome": ("`BLOCK: UNVERIFIABLE_ACQUISITION`", "do not import or send"),
    },
    "Confirmed welcome handoff": {
        "given": ("pending grant", "same list, channel, and purpose", "confirms"),
        "outcome": ("set that grant to `SUBSCRIBED`", "`02-welcome-onboarding`"),
    },
}

contradictions = {
    "unconfirmed subscription": re.compile(r"mark (?:every|all) form submissions? (?:as )?subscribed", re.I),
    "permissionless acquisition": re.compile(r"bought(?:\s+and|\s*,)?\s*scraped addresses are permitted", re.I),
    "lead-magnet inferred consent": re.compile(r"lead[- ]magnet download proves consent", re.I),
}


# Paraphrase-resistant gates: instead of matching one literal phrasing, each
# gate looks for a topic noun co-occurring with a permissive/bypass signal in
# the same sentence, and backs off when a hedge/negation word is present.
# This survives rewordings that dodge the literal `contradictions` regexes
# above while a reviewer's fresh paraphrase can still trip it, because the
# gate keys on intent (what is being permitted) rather than exact wording.

_NEGATION = re.compile(
    r"\b(never|do not|don't|does not|doesn't|only after|only when|not permitted|"
    r"prohibited|before confirm|before confirming|unconfirmed|no hidden|without "
    r"presenting|not proof of|requires? (?:re-)?confirmation|require re-confirmation|"
    r"must (?:be )?(?:re-)?confirm\w*)\b"
)

_SUBSCRIBE_WORD = re.compile(r"\bsubscri\w*\b")
_QUANTIFIED_SIGNUP = re.compile(r"\b(every|all|any)\b.{0,25}\b(signup|sign-up|submission|form)\b")
_AUTO_BYPASS = re.compile(
    r"\bautomatically\b|\bregardless of confirmation\b|\bwithout confirmation\b|"
    r"\bno confirmation (?:needed|required)\b|\bimmediately upon (?:submission|signup)\b"
)

# Source and target are matched independently (not adjacency-anchored) so
# reordered phrasing like "a list we bought from a data broker" still trips
# both conditions.
_SOURCE_ADDRESSES = re.compile(
    r"\b(bought|purchased|rented|scraped|harvested|buy|buys|buying|rent|rents|renting|"
    r"scrape|scrapes|scraping|harvest|harvests|harvesting|third-party|third party|"
    r"unverified|data broker|list broker)\b"
)
_IMPORT_VERB = re.compile(
    r"\b(import(?:ed|ing)?|merge[sd]?|merging|add(?:ed|ing)?|onboard(?:ed|ing)?|include[sd]?|"
    r"bring(?:ing)? in|brought in|pull(?:ed|ing)? in|source[d]? from)\b"
)
_AUDIENCE_TARGET = re.compile(r"\b(audience|subscriber base|mailing list|marketing list|send list|list|lists|addresses|contacts)\b")

_LEAD_MAGNET_NOUN = re.compile(
    r"\b(download(?:ing)?|access(?:ing)?|resource|guide|lead magnet|ebook|e-book|whitepaper|"
    r"checklist|template|freebie|content upgrade|cheat sheet|pdf|tool)\b"
)
_EQUATES_TO = re.compile(
    r"\b(counts as|constitutes|implies|equals|serves as|is treated as|is considered|"
    r"amounts to|equates to|is equivalent to)\b|"
    r"\bis (?:basically |essentially |pretty much )?the same as\b"
)
_CONSENT_NOUN = re.compile(
    r"\bopt(?:ing)?[- ]?in\b|\bconsent\b|\bsubscri\w*\b|\bmarketing permission\b|"
    r"\bnewsletter\b|\bmarketing emails?\b"
)

_CONFIRM_WORD = re.compile(r"\bconfirm\w*\b|\bsubscri\w*\b|\bopts? in\b|\bjoin(?:s|ed|ing)?\b")
_UNIVERSAL_SCOPE = re.compile(
    r"\bevery (?:list|purpose|channel|campaign)\b|\ball (?:our )?(?:lists|purposes|channels|campaigns)\b|"
    r"\beverything (?:we|they) send\b|\beverything\b"
)


def _normalize(text: str) -> str:
    return re.sub(r"[`*_]", "", text.lower())


def _sentences(text: str) -> list[str]:
    normalized = _normalize(text)
    return [s.strip() for s in re.split(r"(?<=[.!?;])\s+|\n+", normalized) if s.strip()]


def _gate(text: str, all_of=(), any_of=(), safe=_NEGATION) -> bool:
    for sentence in _sentences(text):
        if safe.search(sentence):
            continue
        if all_of and not all(p.search(sentence) for p in all_of):
            continue
        if any_of and not all(any(p.search(sentence) for p in group) for group in any_of):
            continue
        return True
    return False


paraphrase_gates = {
    # Closes: "signup implies confirmed subscription" bypass, e.g. "Every
    # signup is automatically added as a confirmed subscriber regardless of
    # confirmation" — any universally-quantified signup paired with an
    # automatic/bypass signal, not just the literal fixture wording.
    "confirmed-subscription-bypass": lambda t: _gate(
        t, all_of=[_SUBSCRIBE_WORD], any_of=[[_QUANTIFIED_SIGNUP], [_AUTO_BYPASS]]
    ),
    # Closes: permitting purchased/rented/scraped/third-party addresses into
    # the sendable audience under any verb (import/merge/add/onboard), not
    # just the fixture's literal "bought...scraped addresses are permitted".
    "prohibited-list-import": lambda t: _gate(
        t, any_of=[[_SOURCE_ADDRESSES], [_IMPORT_VERB], [_AUDIENCE_TARGET]]
    ),
    # Closes: treating lead-magnet access/download as proof of marketing
    # consent, e.g. "Downloading the guide counts as opting in to marketing".
    "lead-magnet-implies-consent": lambda t: _gate(
        t, any_of=[[_LEAD_MAGNET_NOUN], [_EQUATES_TO], [_CONSENT_NOUN]]
    ),
    # Closes: confirming one list/channel/purpose silently granting every
    # other list/channel/purpose, e.g. "Confirming any single list
    # subscribes the contact to every list and purpose".
    "cross-scope-grant-leakage": lambda t: _gate(
        t, all_of=[_CONFIRM_WORD], any_of=[[_UNIVERSAL_SCOPE]]
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
    raise SystemExit("List-growth contract invalid: " + ", ".join(errors))

# False-positive guards: compliant statements a real skill might legitimately
# contain, which must NOT trip the paraphrase gates. Regression case from
# PR #21 review (prohibited-list-import flagged compliant re-confirmation
# language because "before confirm(ing)" required rigid word adjacency).
false_positive_guards = {
    "explicit re-confirmation before import": "Third-party ESP migrations require re-confirmation from every contact before they are added to any list.",
}
for label, sentence in false_positive_guards.items():
    mutated = text + f"\n{sentence}"
    if validate(mutated):
        raise SystemExit(f"False-positive guard failed: '{label}' incorrectly flagged as a violation")

fixtures = {
    "pending outcome": ("matching marketing and welcome", ""),
    "cross-purpose isolation": ("education permission and receipt remain eligible", ""),
    "acquisition decision": ("`BLOCK: UNVERIFIABLE_ACQUISITION`", ""),
    "lead-magnet decision": ("subscribe only when", ""),
    "unconfirmed contradiction": ("", "\nMark every form submission subscribed."),
    "acquisition contradiction": ("", "\nBought and scraped addresses are permitted."),
    "lead-magnet contradiction": ("", "\nLead-magnet download proves consent."),
    "paraphrased auto-subscribe": (
        "",
        "\nEvery signup is automatically added as a confirmed subscriber regardless of confirmation.",
    ),
    "paraphrased list purchase": (
        "",
        "\nPurchased and rented lists may be imported into the marketing audience.",
    ),
    "paraphrased lead-magnet consent": (
        "",
        "\nDownloading the guide counts as opting in to marketing.",
    ),
    "paraphrased cross-scope grant": (
        "",
        "\nConfirming any single list subscribes the contact to every list and purpose.",
    ),
    "novel auto-subscribe paraphrase": (
        "",
        "\nAnyone who fills out any signup form becomes a confirmed subscriber automatically.",
    ),
    "novel third-party import paraphrase": (
        "",
        "\nThird-party marketing lists can be merged into our subscriber base without additional verification.",
    ),
}
for label, (deleted_text, appended_text) in fixtures.items():
    mutated = text.replace(deleted_text, "", 1) + appended_text
    if mutated == text:
        raise SystemExit(f"Behavior fixture missing: {label}")
    if not validate(mutated):
        raise SystemExit(f"Behavior fixture accepted: {label}")

print(f"list-growth consent contract OK: {len(trace_requirements)} decision traces; {len(fixtures)} invalid behaviors rejected")
