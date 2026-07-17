---
name: 03-lead-nurture-education
description: Build a multi-step nurture that educates permissioned leads and advances them through a considered purchase journey.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Lead Nurture and Educational Drip

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A nurture sequence uses triggers, segmentation, and progressively relevant content to move a lead from initial interest toward a qualified next step. [HUB-WF-01][HUB-AUTO-01]

## When and where
- Trigger from a known action such as a form submission, content request, webinar registration, product inquiry, or lifecycle-stage change. [HUB-WF-01][BRAZE-TRIG-01]
- Use only contacts eligible for marketing, and route high-intent responses or threshold events to the appropriate sales or success owner. [HUB-AUTO-01][HUB-B2B-01]

## How
- Deliver the promised asset or answer immediately, then sequence education, use cases, verified proof, objection handling, and a progressively stronger CTA. [MC-FOLLOW-01][HUB-B2B-01]
- Segment by role, industry, company context, lifecycle stage, behavior, or declared need; do not use a single generic sequence for materially different buyers. [HUB-B2B-01][MC-SEG-01]
- Use two to five follow-ups only as a starting range, adjust spacing to the buying cycle, and stop when the person converts, replies, opts out, or becomes ineligible. [MC-FOLLOW-01][HUB-WF-01]
- Give every email one job and one primary next step, such as read, compare, register, reply, book, trial, or purchase. [BRAZE-STRAT-01]
- Personalize only from reliable CRM or behavioral fields and provide safe fallbacks for missing values. [LIT-QA-01][BRAZE-STRAT-01]
- Measure qualified replies, MQL/SQL movement, meetings, opportunities, pipeline sourced/influenced, deal velocity, and conversions rather than opens alone. [HUB-B2B-01][LIT-MPP-01]

## Do / Don't quick reference
**Do**
- Deliver the promised asset or answer immediately. [MC-FOLLOW-01][HUB-B2B-01]
- Segment by role, industry, lifecycle stage, or declared need. [HUB-B2B-01][MC-SEG-01]
- Give every email one job and one primary next step. [BRAZE-STRAT-01]
- Route high-intent responses to the right sales or success owner. [HUB-AUTO-01][HUB-B2B-01]
- Measure qualified replies, pipeline movement, and conversions. [HUB-B2B-01][MC-CONV-01]

**Don't**
- Don't run one generic sequence for materially different buyers. [HUB-B2B-01][MC-SEG-01]
- Don't continue after the person converts, replies, or opts out. [MC-FOLLOW-01][HUB-WF-01]
- Don't exceed a small number of value-adding follow-ups; two to five is the starting range to test. [MC-FOLLOW-01]
- Don't personalize from unreliable fields or without safe fallbacks. [LIT-QA-01][BRAZE-STRAT-01]

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
