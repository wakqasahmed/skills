---
name: 08-browse-abandonment
description: Create a lighter behavior-triggered reminder for identifiable, consented visitors who viewed products but did not advance.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Browse Abandonment

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A browse-abandonment flow follows a product view without cart or checkout activity, so it must be lighter than cart recovery. [KL-BROWSE-01]

## When and where
- Trigger only when viewed-product tracking can lawfully identify the visitor and the person is eligible for marketing. [KL-BROWSE-01][ICO-02]
- Do not send when the person has since added to cart, started checkout, purchased, or recently received the same browse flow. [KL-BROWSE-01]

## How
- Use the viewed product as context, but write as a helpful reminder or discovery message rather than claiming the person “forgot” a cart. [KL-BROWSE-01]
- Include the viewed item and, when supported by reliable catalog data, related alternatives or helpful category content. [KL-BROWSE-01][BRAZE-STRAT-01]
- Use Klaviyo’s recommended protections as a baseline: zero purchases, zero checkout starts, zero add-to-cart events since entry, and no repeat entry in the prior 30 days. [KL-BROWSE-01]
- Apply frequency controls so browse messages do not collide with welcome, cart, launch, or promotional sends. [BRAZE-STRAT-01][HUB-WF-01]
- Measure product revisits, add-to-cart rate, checkout starts, purchases, revenue, unsubscribes, and complaints. [MC-GA-01][MC-CONV-01]

## Do / Don't quick reference
**Do**
- Keep the touch lighter than cart recovery. [KL-BROWSE-01]
- Frame the message as a helpful reminder or discovery aid. [KL-BROWSE-01]
- Apply the baseline protections: no purchases, checkout starts, or add-to-cart events since entry, and no re-entry within 30 days. [KL-BROWSE-01]
- Apply frequency controls against welcome, cart, launch, and promotional sends. [BRAZE-STRAT-01][HUB-WF-01]

**Don't**
- Don't claim the person "forgot" a cart they never created. [KL-BROWSE-01]
- Don't send unless tracking lawfully identifies the visitor and they are eligible for marketing. [KL-BROWSE-01][ICO-02]
- Don't recommend alternatives from unreliable catalog data. [KL-BROWSE-01][BRAZE-STRAT-01]
- Don't re-enter recent recipients into the same flow. [KL-BROWSE-01]

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
