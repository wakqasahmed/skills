---
name: 18-jurisdiction-compliance-routing
description: Route email-marketing work by sender and recipient jurisdiction before drafting, with operational checkpoints for the US, UK, EEA, Canada, and unresolved locations.
version: 1.0.0
last_reviewed: 2026-07-16
---

# Jurisdiction-Aware Email Compliance Routing

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`) and before drafting, reviewing, approving, or scheduling recipient-facing email content. It provides operational routing, not legal advice; refer unresolved applicability, legal-basis, or exception questions to qualified counsel. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]

## Collect routing facts first
- Record each recipient's country or region, the sender's establishment, the sending-system location, and any known location or sector factors that could change the applicable rule. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]
- Record the message's primary purpose, recipient type, address source, signup language, consent or other documented basis, prior customer relationship, and current suppression status. [FTC-01][ICO-02][EU-EC-01][CRTC-CASL-01]
- Keep recipients with different routing results out of one send until each group has passed its applicable checks. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]
- Do not draft recipient-facing marketing content until all routing facts are complete and the routing result is `SEND`. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]

## Route the recipient group using sender and recipient facts
- **US:** Apply the CAN-SPAM commercial-message classification, identity, address, truthful-header/subject, and opt-out operational checks; do not present this US route as a universal permission standard. [FTC-01]
- **UK:** Verify the applicable PECR and UK-GDPR route for the recipient and message, including whether any claimed consent or customer exception is documented; route unresolved cases to qualified counsel. [ICO-01][ICO-02]
- **EEA:** Identify the relevant EEA member state, document the proposed GDPR processing ground and any applicable national requirements, and obtain qualified counsel when the ground, balancing assessment, or local rule is unresolved. [EU-EC-01][EU-EC-02]
- **Canada:** Treat a commercial electronic message as a CASL routing case when the recipient is in Canada or it is sent using a computer system located in Canada. For a Canada-to-non-Canadian recipient group, return `BLOCK` until qualified counsel verifies any limited outbound exemption and recipient-jurisdiction requirements; otherwise document the consent relied on, sender identification, and unsubscribe mechanism before proceeding. [CRTC-CASL-01][CRTC-CASL-02]
- **Unknown or conflicting jurisdiction:** Return `HOLD` only while the team can collect the missing routing fact; return `BLOCK` when jurisdiction, legal basis, or applicable exception cannot be verified, and do not draft or schedule the recipient group. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]

## Mandatory output
Return all of the following before campaign-specific drafting:
1. Recipient group and jurisdiction facts, including unknowns.
2. Message classification and documented consent or other proposed basis.
3. Selected routing path: US, UK, EEA, Canada, or unknown/conflicting, based on sender and recipient facts.
4. Applicable operational checks and any required counsel review.
5. Recipient groups excluded or separated from the send.
6. Final `SEND`, `HOLD`, or `BLOCK` decision, with the unresolved fact or counsel question where applicable.
7. A source list containing every citation ID used.

## Agent restrictions
- Never describe US, UK, EEA, or Canadian requirements as universally applicable. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]
- Never decide an unresolved legal basis, statutory exception, or cross-border applicability question; return `BLOCK` and direct it to qualified counsel. [ICO-01][EU-EC-01][CRTC-CASL-01]
- Never turn a `HOLD` or `BLOCK` routing result into recipient-facing copy. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]
