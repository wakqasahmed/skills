---
name: 09-post-purchase-customer-success
description: Create lifecycle messages after purchase that improve experience, adoption, loyalty, and repeat purchase without confusing service and marketing mail.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Post-Purchase and Customer Success

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A post-purchase flow supports the customer after an order and can build loyalty, product success, reviews, and repeat purchase. [KL-POST-01]

## When and where
- Trigger from placed, fulfilled, delivered, or product-usage events according to the job of the email. [KL-POST-01][KL-XSELL-01]
- Keep receipts, shipping notices, account updates, and other essential information in the transactional stream; place optional promotions in the marketing stream. [BRAZE-TRANS-01][MC-PERM-01]

## How
- Branch by first-time vs repeat buyer, product/category, order value, delivery state, loyalty tier, and likely usage needs. [KL-POST-01][KL-VIP-01]
- Sequence only relevant jobs: gratitude/expectations, setup or care education, support resources, review request after adequate experience, and later cross-sell or replenishment. [KL-POST-01][KL-XSELL-01][KL-REPLEN-01]
- Do not send a review or cross-sell before the customer is reasonably likely to have received and used the product. [KL-XSELL-01][KL-POST-01]
- Suppress product recommendations already purchased or incompatible with the order. [KL-XSELL-01]
- Measure support deflection, activation/usage, review completion, repeat purchase, time to second order, revenue, refund/return rate, and complaints. [BRAZE-METRIC-01][MC-CONV-01]

## Do / Don't quick reference
**Do**
- Branch by first-time vs repeat buyer, product, order value, and delivery state. [KL-POST-01][KL-VIP-01]
- Time each message to the fulfillment, delivery, or usage event it depends on. [KL-POST-01][KL-XSELL-01]
- Keep receipts, shipping, and account notices in the transactional stream. [BRAZE-TRANS-01][MC-PERM-01]
- Measure repeat purchase, time to second order, and support deflection. [BRAZE-METRIC-01][MC-CONV-01]

**Don't**
- Don't request a review or cross-sell before the customer has received and used the product. [KL-XSELL-01][KL-POST-01]
- Don't recommend products already purchased or incompatible with the order. [KL-XSELL-01]
- Don't blend promotions into essential service messages. [BRAZE-TRANS-01][FTC-01]

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
