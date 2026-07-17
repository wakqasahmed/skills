---
name: 11-cross-sell-upsell
description: Recommend a relevant complementary or higher-value product using verified purchase, fulfillment, or behavior data.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Cross-Sell and Upsell

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A cross-sell recommends a complementary product, while an upsell recommends a more valuable alternative or expansion based on actual context. [KL-XSELL-01]

## When and where
- Use placed or fulfilled order events for post-purchase cross-sell, and use viewed-product or other high-intent behavior only when the recommendation is genuinely relevant. [KL-XSELL-01]
- Wait until the customer is likely to have received the original order when the recommendation depends on product experience; Klaviyo’s default example uses 14 days after fulfillment as a testable baseline. [KL-XSELL-01]

## How
- Filter by purchased/viewed category, compatibility, plan, lifecycle stage, and prior purchases so recommendations are specific. [KL-XSELL-01]
- Exclude already purchased, unavailable, incompatible, or recently returned items. [KL-XSELL-01][FTC-01]
- Explain the relationship between the original item and the recommendation instead of showing an arbitrary bestseller grid. [KL-XSELL-01]
- Use one primary recommendation set and CTA, with accurate price, availability, and terms. [FTC-01][BRAZE-STRAT-01]
- Measure attach rate, average order value, incremental revenue or margin, repeat purchase, returns, unsubscribes, and complaints. [MC-CONV-01][BRAZE-METRIC-01]

## Do / Don't quick reference
**Do**
- Base recommendations on placed or fulfilled orders or genuine high-intent behavior. [KL-XSELL-01]
- Wait until the customer likely has the original order; 14 days after fulfillment is a testable baseline. [KL-XSELL-01]
- Explain the relationship between the original item and the recommendation. [KL-XSELL-01]
- Show accurate price, availability, and terms with one primary CTA. [FTC-01][BRAZE-STRAT-01]

**Don't**
- Don't show an arbitrary bestseller grid as a recommendation. [KL-XSELL-01]
- Don't recommend already purchased, unavailable, incompatible, or recently returned items. [KL-XSELL-01][FTC-01]
- Don't stack several competing offers and CTAs in one message. [BRAZE-CTA-01][BRAZE-STRAT-01]

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
