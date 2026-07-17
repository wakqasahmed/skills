---
name: 05-product-launch
description: Plan an announcement sequence that explains a new product or feature and drives adoption, trials, demos, or purchases.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Product or Feature Launch Campaign

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A launch campaign coordinates a sequence of messages that explains what is new, who it is for, why it matters, and what the recipient should do next. [HUB-LAUNCH-01][BRAZE-STRAT-01]

## When and where
- Use it when the product, pricing, availability, support readiness, landing page, and claims have been verified by the responsible teams. [FTC-01][LIT-QA-01]
- Separate existing customers, prospects, waitlist members, partners, and incompatible users so each audience receives accurate positioning. [MC-SEG-01][BRAZE-STRAT-01]

## How
- Build a sequence from the evidence-backed launch pattern: preview or early access where appropriate, launch announcement, use-case or proof message, and a final reminder only when a real deadline or availability constraint exists. [HUB-LAUNCH-01][FTC-01]
- Lead with the recipient problem and outcome, then explain the differentiator, proof, availability, pricing or eligibility, and next step. [HUB-LAUNCH-01]
- Personalize by use case, plan, prior product behavior, or role, and suppress recipients for whom the feature is unavailable or irrelevant. [MC-SEG-01][HUB-WF-01]
- Keep every claim traceable to approved product documentation, customer evidence, or legal/compliance review. [FTC-01]
- Measure activation/adoption, trials, demos, upgrades, purchases, pipeline, revenue, support contacts, complaints, and retention after adoption. [BRAZE-METRIC-01][HUB-B2B-01]
- Test positioning, proof format, CTA, and sequence timing one variable at a time. [MC-AB-01][HUB-AB-01]

## Do / Don't quick reference
**Do**
- Verify product, pricing, availability, support readiness, and claims before scheduling. [FTC-01][LIT-QA-01]
- Lead with the recipient problem and outcome, then differentiator and proof. [HUB-LAUNCH-01]
- Separate customers, prospects, waitlist, partners, and incompatible users. [MC-SEG-01][BRAZE-STRAT-01]
- Keep every claim traceable to approved documentation or verified evidence. [FTC-01]

**Don't**
- Don't send a final reminder unless a real deadline or availability constraint exists. [HUB-LAUNCH-01][FTC-01]
- Don't announce to users for whom the product is unavailable or irrelevant. [MC-SEG-01][HUB-WF-01]
- Don't invent proof, benchmarks, or performance claims. [FTC-01]
- Don't test several launch variables at once. [MC-AB-01][HUB-AB-01]

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
