---
name: 13-winback-reengagement-sunset
description: Re-engage inactive customers or subscribers once, then suppress non-responders to protect relevance and deliverability.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Winback, Re-Engagement, and Sunset

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A winback flow targets past customers after a meaningful lapse; a sunset flow makes a final permission/value check and suppresses contacts who remain unresponsive. [KL-WINBACK-01][KL-SUNSET-01]

## When and where
- Define inactivity from the expected purchase or engagement cycle, not a universal number of days. [KL-WINBACK-01][BRAZE-STRAT-01]
- Use clicks, purchases, site/app activity, replies, or other reliable signals; do not classify engagement from opens alone. [LIT-MPP-01][KL-NEVER-01]

## How
- Personalize with the verified prior relationship, product/category, benefit, new value, or preference options; do not pretend the recipient was recently active. [KL-WINBACK-01][FTC-01]
- Use a short sequence with a clear value reminder, a relevant reason to return, and a final preference/permission decision. [KL-WINBACK-01][KL-SUNSET-01]
- Do not default to a discount; test an incentive only when economics and brand strategy support it. [MC-AB-01][MC-CONV-01]
- Suppress contacts who do not engage after the final attempt, and immediately suppress unsubscribes, complaints, and hard bounces. [KL-SUNSET-01][KL-NEVER-01][GMAIL-01]
- Measure reactivation, purchase, retained revenue, preference updates, suppression volume, complaint rate, and later retention. [BRAZE-METRIC-01][MC-CONV-01]

## Do / Don't quick reference
**Do**
- Define inactivity from the expected purchase or engagement cycle. [KL-WINBACK-01][BRAZE-STRAT-01]
- Classify engagement from clicks, purchases, activity, or replies. [LIT-MPP-01][KL-NEVER-01]
- Personalize from the verified prior relationship and offer preference options. [KL-WINBACK-01]
- Make one deliberate final permission/value check, then suppress non-responders. [KL-SUNSET-01][KL-NEVER-01]

**Don't**
- Don't pretend the recipient was recently active. [KL-WINBACK-01][FTC-01]
- Don't default to a discount; test incentives only when economics support them. [MC-AB-01][MC-CONV-01]
- Don't keep mailing contacts who ignored the final attempt. [KL-SUNSET-01][KL-NEVER-01]
- Don't use a universal day-count as the inactivity definition. [KL-WINBACK-01][BRAZE-STRAT-01]

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
