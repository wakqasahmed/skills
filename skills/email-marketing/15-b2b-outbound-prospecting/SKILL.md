---
name: 15-b2b-outbound-prospecting
description: Create lawful, low-volume, relevant business outreach with strict suppression, identity, and reply controls.
version: 1.0.0
last_reviewed: 2026-07-15
---

# B2B Outbound Prospecting

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
B2B outbound is direct commercial outreach to a business contact; it is not automatically permission-based and must pass jurisdiction-specific legal and platform checks before use. [ICO-03][FTC-01]

## When and where
- Determine whether the address belongs to a corporate subscriber or an identifiable individual and document the lawful basis, source, purpose, and jurisdiction before sending. [ICO-03][ICO-04]
- Do not treat CAN-SPAM compliance as proof that outreach is lawful everywhere, and do not use bought, scraped, or unverifiable lists. [FTC-01][ICO-04][MC-LISTS-01]
- Use a real person or clearly identified business sender, an accurate subject, and a functioning reply path. [FTC-01]

## How
- Segment narrowly by industry, role, company context, and a verified business trigger; explain why the message is relevant to that recipient. [HUB-B2B-01]
- Lead with a concrete problem, useful observation, or resource, then ask for one low-friction next step; do not manufacture familiarity or use deceptive `Re:`/`Fwd:` framing. [FTC-01][HUB-B2B-01]
- Use a small number of value-adding follow-ups, with two to five as a broad ceiling to test rather than a mandate; stop immediately on reply, objection, opt-out, or ineligibility. [MC-FOLLOW-01][ICO-03]
- Include a clear opt-out and maintain a do-not-contact list even where corporate-email rules are less strict. [ICO-01][ICO-03][FTC-01]
- Measure positive reply rate, meetings, qualified opportunities, pipeline sourced/influenced, deal velocity, opt-outs, complaints, and domain reputation. [HUB-B2B-01][GMAIL-03]

## Do / Don't quick reference
**Do**
- Document the lawful basis, address source, purpose, and jurisdiction, distinguishing corporate subscribers from identifiable individuals. [ICO-03][ICO-04]
- Segment narrowly and explain why the message is relevant to that recipient. [HUB-B2B-01]
- Send from a real, clearly identified person or business with a working reply path. [FTC-01]
- Include a clear opt-out and maintain a do-not-contact list everywhere. [ICO-01][ICO-03][FTC-01]

**Don't**
- Don't use bought, scraped, or unverifiable lists. [MC-LISTS-01][ICO-04]
- Don't treat CAN-SPAM compliance as proof the outreach is lawful in every jurisdiction. [FTC-01][ICO-03]
- Don't manufacture familiarity or use deceptive `Re:`/`Fwd:` framing. [FTC-01]
- Don't continue follow-ups after a reply, objection, or opt-out. [MC-FOLLOW-01][ICO-03]

## Mandatory output
Return all of the following:
1. Campaign objective and one primary business KPI.
2. Audience, eligibility, exclusions, and consent/lawful-basis note.
3. Trigger or send schedule, including exit and suppression rules.
4. Message map showing the job of each email, subject-line hypotheses, body outline, personalization, and one primary CTA.
5. Measurement plan with UTMs, conversion event, attribution window, and guardrail metrics.
6. Test plan that changes one major variable at a time and names the winning metric.
7. Pre-send QA checklist and a final `SEND`, `HOLD`, or `BLOCK` decision.
8. A source list containing every citation ID used.

## Agent restrictions
- Never invent product facts, customer proof, discounts, deadlines, scarcity, legal permission, or performance claims. [FTC-01][BRAZE-STRAT-01]
- Never infer consent merely because an address exists; verify the permitted purpose, channel, source, jurisdiction, and suppression status. [ICO-01][ICO-02][HUB-CONSENT-01]
- Never optimize for opens alone; use clicks, conversions, revenue, retention, qualified replies, or pipeline as the primary outcome. [LIT-MPP-01][MC-CONV-01][BRAZE-METRIC-01]
- Never claim a universal best send time; use recipient-level optimization or a controlled timing test. [MC-TIME-01][MC-AB-01]
- Never send until authentication, suppression, tracking, rendering, links, personalization fallbacks, and accessibility checks pass. [GMAIL-01][YAHOO-01][LIT-QA-01][LIT-TEST-01]
