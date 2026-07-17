---
name: 16-inventory-price-alert
description: Create opt-in or behavior-triggered inventory and price alerts tied to verified catalog changes.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Back-in-Stock, Low-Inventory, and Price-Drop Alert

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
These alerts notify a shopper when a requested item returns, a relevant item reaches a real stock threshold, or a previously viewed item has a verified price drop. [KL-STOCK-01][KL-LOWSTOCK-01][KL-PRICE-01]

## When and where
- For back-in-stock, trigger only for people who explicitly requested notification for that item and send when inventory actually returns. [KL-STOCK-01]
- For low-inventory or price-drop campaigns, use eligible identifiable shoppers with relevant viewed/checkout behavior and accurate catalog data. [KL-LOWSTOCK-01][KL-PRICE-01]

## How
- Send promptly after the qualifying inventory or price event; low-inventory guidance recommends no unnecessary delay. [KL-LOWSTOCK-01]
- Include the exact product/variant, current price, availability state, and direct product CTA; do not imply a false sellout or discount. [FTC-01][KL-PRICE-01]
- Suppress people who already purchased, recently purchased, face unavailable inventory, or no longer meet the trigger conditions. [KL-LOWSTOCK-01][KL-PRICE-01]
- Avoid repeated alerts when inventory may disappear quickly; one timely message is safer than an uncontrolled sequence. [KL-LOWSTOCK-01]
- Measure click-to-product, conversion, revenue/margin, time-to-purchase, out-of-stock clicks, unsubscribes, and complaints. [MC-GA-01][MC-CONV-01]

## Do / Don't quick reference
**Do**
- Send back-in-stock alerts only to people who explicitly requested them for that item. [KL-STOCK-01]
- Send promptly after the verified inventory or price event. [KL-LOWSTOCK-01]
- Show the exact product variant, current price, and availability state. [KL-PRICE-01][FTC-01]
- Suppress recipients who purchased or no longer meet the trigger conditions. [KL-LOWSTOCK-01][KL-PRICE-01]

**Don't**
- Don't imply a false sellout, threshold, or discount. [FTC-01]
- Don't send repeated alerts when inventory may disappear quickly; one timely message is safer. [KL-LOWSTOCK-01]
- Don't alert from stale or unverified catalog data. [KL-LOWSTOCK-01][KL-PRICE-01]

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
