#!/usr/bin/env python3
"""Check non-negotiable event-webinar rules independently of outcome scoring."""
from pathlib import Path


SKILL = Path(__file__).parents[1] / "SKILL.md"
RULES = (
    "Provide both Google Calendar and ICS options where possible.",
    "Stop invitation emails after registration and stop reminders after cancellation or ineligibility.",
    "After the event, segment attendees and no-shows; send the recording or resources and one clear next-step CTA.",
    "Never invent product facts, customer proof, discounts, deadlines, scarcity, legal permission, or performance claims.",
    "Never infer consent merely because an address exists; verify the permitted purpose, channel, source, jurisdiction, and suppression status.",
    "Never send until authentication, suppression, tracking, rendering, links, personalization fallbacks, and accessibility checks pass.",
)


def main() -> int:
    skill = SKILL.read_text()
    missing = [rule for rule in RULES if rule not in skill]
    if missing:
        print("FAIL: event-webinar static contract")
        print("\n".join(f"missing rule: {rule}" for rule in missing))
        return 1
    print(f"PASS: event-webinar static contract ({len(RULES)} rules)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
