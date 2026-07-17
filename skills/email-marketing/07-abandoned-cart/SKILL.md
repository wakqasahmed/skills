---
name: 07-abandoned-cart
description: Create a behavior-triggered recovery sequence for identifiable shoppers who started checkout but did not purchase.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Abandoned Cart and Checkout Recovery

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
An abandoned-cart flow reminds an identifiable shopper about a checkout they started but did not complete. [KL-CART-01]

## When and where
- Trigger from checkout-started or equivalent high-intent behavior, not from a mere page view. [KL-CART-01][KL-BROWSE-01]
- Require appropriate marketing permission for promotional reminders and suppress anyone who completes the order. [ICO-02][KL-CART-01]

## How
- Use a first-delay baseline of two to four hours after checkout starts and a second reminder roughly 20–48 hours later; adjust for consideration cycle and test. [KL-CART-01]
- Populate the exact cart items, images, titles, quantities, prices, and a functioning return-to-cart link. [KL-CART-01]
- Keep the first message helpful and friction-reducing; do not invent a discount, stock threat, or expiry. [FTC-01]
- Branch by new vs repeat customer, cart value, product category, geography, or known checkout obstacle when data is reliable. [KL-CART-01][BRAZE-STRAT-01]
- Exit immediately on purchase, opt-out, complaint, invalid inventory, or cart expiry. [HUB-WF-01][GMAIL-01]
- Measure recovered orders, recovered revenue, conversion after send/click, margin after incentives, complaint/unsubscribe rate, and overlap with other flows. [MC-CONV-01][BRAZE-METRIC-01]

## Do / Don't quick reference
**Do**
- Trigger from checkout-started or equivalent high-intent behavior. [KL-CART-01]
- Use the 2–4 hour first-reminder and 20–48 hour second-reminder baseline, then test. [KL-CART-01]
- Show the exact cart items, quantities, prices, and a working return-to-cart link. [KL-CART-01]
- Exit immediately on purchase, opt-out, complaint, or invalid inventory. [HUB-WF-01][GMAIL-01]

**Don't**
- Don't invent a discount, stock threat, or expiry to force urgency. [FTC-01]
- Don't trigger cart recovery from a mere page view. [KL-CART-01][KL-BROWSE-01]
- Don't send promotional reminders without marketing permission. [ICO-02]
- Don't let cart messages collide with browse, welcome, or promotional flows unchecked. [BRAZE-STRAT-01][HUB-WF-01]

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
