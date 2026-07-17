---
name: 04-promotional-offer
description: Create a targeted commercial campaign for a real offer, sale, seasonal promotion, or conversion event.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Promotional and Sales Campaign

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A promotional email presents a commercial offer and asks an eligible recipient to take a conversion action. [BRAZE-TRANS-01]

## When and where
- Use it only for recipients permitted to receive marketing and only when the offer is relevant to the selected segment. [MC-PERM-01][MC-SEG-01]
- Keep promotional traffic distinct from essential transactional messages so service information is not obscured by marketing. [BRAZE-TRANS-01]

## How
- State the offer, eligibility, material terms, price/discount, expiry, and exclusions accurately; never fabricate scarcity or use a deceptive subject. [FTC-01][MC-SUBJ-01]
- Segment by lifecycle stage, purchase history, product/category interest, geography, and engagement; exclude recent purchasers when the offer would frustrate them. [MC-SEG-01][BRAZE-STRAT-01]
- Use one primary CTA that matches the landing page, and keep the message understandable without images. [LIT-ACCESS-01][LIT-QA-01]
- Increase frequency or audience size gradually, especially around holidays, and offer a preference or pause option rather than forcing recipients to unsubscribe entirely. [BRAZE-HOLIDAY-01][BRAZE-STRAT-01]
- Do not automatically resend to non-openers; open data can be inaccurate and repeated sends can increase complaints or unsubscribes. [LIT-MPP-01][MC-RESEND-01]
- Measure delivered revenue, conversion rate, profit or contribution margin, average order value, unsubscribe/complaint rate, and landing-page conversion. [MC-CONV-01][MC-GA-01][BRAZE-METRIC-01]
- Test one variable such as offer framing, subject, CTA, content, or send time, and select the winner using the business outcome closest to revenue. [MC-AB-01][HUB-AB-01]

## Do / Don't quick reference
**Do**
- State the offer, eligibility, material terms, price, and expiry accurately. [FTC-01]
- Exclude recent purchasers when the offer would frustrate them. [MC-SEG-01][BRAZE-STRAT-01]
- Match the primary CTA to the landing page and verify both. [LIT-QA-01][MC-GA-01]
- Increase frequency and audience size gradually, especially around holidays. [BRAZE-HOLIDAY-01]
- Measure delivered revenue, margin, and conversion, not clicks alone. [MC-CONV-01][BRAZE-METRIC-01]

**Don't**
- Don't fabricate scarcity, deadlines, or discounts. [FTC-01][MC-SUBJ-01]
- Don't automatically resend to non-openers. [MC-RESEND-01][LIT-MPP-01]
- Don't force a full unsubscribe when a preference or pause option would do. [BRAZE-HOLIDAY-01][BRAZE-STRAT-01]
- Don't use a subject or preview that misrepresents the offer. [FTC-01][MC-SUBJ-01]

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
