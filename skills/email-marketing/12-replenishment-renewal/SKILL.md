---
name: 12-replenishment-renewal
description: Create repeat-purchase and subscription or membership renewal sequences based on real consumption or expiry timing.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Replenishment and Renewal

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A replenishment flow reminds a customer near an observed repurchase point, while a renewal flow helps a subscriber act before a real expiry or renewal date. [KL-REPLEN-01][MC-RENEW-01]

## When and where
- Derive replenishment timing from actual product- and customer-level buying cycles rather than a generic interval. [KL-REPLEN-01]
- Trigger renewal messages from the authoritative contract, membership, subscription, or expiry date and keep billing/service notices distinct from optional promotions. [MC-RENEW-01][BRAZE-TRANS-01]

## How
- For renewal, use Mailchimp’s published baseline when the business cycle supports it: a soft reminder 45–60 days before expiry, a stronger reminder at 30 days, a deadline alert at 7–10 days, and a final notice 1–3 days before. [MC-RENEW-01]
- State the item or plan, renewal/expiry date, price and material terms, consequences of action or inaction, and the exact CTA. [FTC-01][MC-RENEW-01]
- Stop or change the sequence immediately after renewal, repurchase, cancellation, opt-out, or ineligibility. [HUB-WF-01]
- Branch by product consumption cycle, plan, tenure, loyalty tier, payment state, or contract owner using verified data. [KL-REPLEN-01][KL-VIP-01]
- Measure repeat purchase or renewal rate, retained revenue, churn, timing-to-renew, margin, support contacts, and complaints. [BRAZE-METRIC-01][MC-CONV-01]

## Do / Don't quick reference
**Do**
- Derive replenishment timing from actual product and customer buying cycles. [KL-REPLEN-01]
- Trigger renewals from the authoritative contract, membership, or expiry date. [MC-RENEW-01]
- Use the published renewal baseline: 45–60 days out, 30 days, 7–10 days, and 1–3 days before expiry. [MC-RENEW-01]
- State the plan, date, price, material terms, and consequences of action or inaction. [FTC-01][MC-RENEW-01]
- Stop immediately after renewal, repurchase, cancellation, or opt-out. [HUB-WF-01]

**Don't**
- Don't use a generic interval in place of observed consumption cycles. [KL-REPLEN-01]
- Don't mix billing or service notices with optional promotions. [BRAZE-TRANS-01]
- Don't invent an expiry or deadline that the authoritative system does not show. [FTC-01]

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
