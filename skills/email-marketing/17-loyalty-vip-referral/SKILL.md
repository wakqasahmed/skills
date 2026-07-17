---
name: 17-loyalty-vip-referral
description: Recognize high-value customers and ask for referrals at relevant moments with transparent incentives and measurable attribution.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Loyalty, VIP, and Referral Campaign

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A loyalty/VIP campaign recognizes high-value customers, while a referral campaign asks satisfied customers to introduce qualified new customers. [KL-VIP-01][MC-REF-01]

## When and where
- Define VIP status from verified recency, frequency, spend, tenure, tier, or strategic value, and update the segment dynamically. [KL-VIP-01][BRAZE-STRAT-01]
- Ask for referrals after a positive, completed experience or demonstrated loyalty, not before the customer has received value. [MC-REF-01][KL-POST-01]

## How
- Give VIPs relevant recognition such as early access, exclusive content, personalized bundles, or surveys rather than merely increasing message volume. [KL-VIP-01]
- State referral eligibility, incentive, attribution, expiry, limits, and fraud/abuse rules accurately for both referrer and referred customer. [FTC-01][MC-REF-01]
- Segment referral asks by customer behavior, preferences, and engagement, and coordinate timing with other campaigns. [MC-REF-01]
- Use trackable referral codes or links and monitor which sources create real sales and valuable repeat customers. [MC-REF-02]
- Measure referral participation, referred conversion, cost per acquired customer, referred-customer value/retention, VIP repeat purchase, incremental margin, fraud, opt-outs, and complaints. [MC-REF-02][BRAZE-METRIC-01]

## Do / Don't quick reference
**Do**
- Define VIP status from verified recency, frequency, spend, tenure, or tier, and update it dynamically. [KL-VIP-01][BRAZE-STRAT-01]
- Recognize VIPs with early access, exclusive content, or personalized value rather than more volume. [KL-VIP-01]
- State referral eligibility, incentive, attribution, expiry, limits, and fraud rules for both parties. [FTC-01][MC-REF-01]
- Use trackable referral codes and measure real sales and repeat-customer value. [MC-REF-02]

**Don't**
- Don't ask for a referral before the customer has received value. [MC-REF-01][KL-POST-01]
- Don't treat increased email volume as a loyalty reward. [KL-VIP-01]
- Don't hide incentive expiry, limits, or eligibility conditions. [FTC-01][MC-REF-01]
- Don't run referral incentives without fraud and abuse monitoring. [MC-REF-01][MC-REF-02]

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
