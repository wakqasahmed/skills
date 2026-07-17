---
name: 10-review-feedback-survey
description: Request honest reviews or structured feedback after an appropriate experience and route responses into service and learning workflows.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Review, Feedback, and Survey Request

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A review or feedback email asks a customer to evaluate a completed experience so the organization can improve and, where permitted, build social proof. [KL-POST-01]

## When and where
- Trigger after delivery, service completion, event attendance, support resolution, or enough product-usage time to form a real opinion. [KL-POST-01][HUB-EVENT-01]
- Use a service survey for operational feedback and a marketing review request only when the recipient is eligible for that communication. [BRAZE-TRANS-01][ICO-02]

## How
- Ask for an honest review or specific feedback; never condition a reward on a positive rating or suppress legitimate negative feedback. [KL-POST-01][FTC-01]
- Keep the request focused, explain how long it takes, and use one direct review or survey CTA. [BRAZE-STRAT-01]
- Personalize from the actual order, service, event, or support case and verify every dynamic field. [LIT-QA-01]
- Route poor experiences or urgent comments to support with consent-aware follow-up, and request separate permission before republishing identifiable testimonials. [ICO-02][FTC-01]
- Measure response rate, completion rate, review publication, issue-resolution rate, sentiment/category trends, and downstream retention; do not optimize to positive ratings alone. [BRAZE-METRIC-01]

## Do / Don't quick reference
**Do**
- Trigger only after delivery, completion, or enough usage to form a real opinion. [KL-POST-01][HUB-EVENT-01]
- Say how long the request takes and use one direct review or survey CTA. [BRAZE-STRAT-01]
- Personalize from the actual order, service, event, or support case. [LIT-QA-01]
- Route poor experiences to support with consent-aware follow-up. [ICO-02][FTC-01]
- Get separate permission before republishing identifiable testimonials. [ICO-02][FTC-01]

**Don't**
- Don't condition a reward on a positive rating. [KL-POST-01][FTC-01]
- Don't suppress or filter out legitimate negative feedback. [KL-POST-01][FTC-01]
- Don't send with unverified dynamic order or case fields. [LIT-QA-01]
- Don't optimize the program to positive ratings alone. [BRAZE-METRIC-01]

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
