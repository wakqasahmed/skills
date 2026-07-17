---
name: 01-newsletter-editorial
description: Plan and optimize recurring newsletters whose primary job is education, curation, trust, or audience engagement.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Newsletter and Editorial Email

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A newsletter is a recurring permission-based editorial message used to maintain a useful relationship, share updates, and move readers toward a measurable next action. [MC-NEWS-01][MC-PERM-01]

## When and where
- Use it when the audience has explicitly subscribed to ongoing content and the brand can sustain the promised topic and cadence. [MC-PERM-01][ICO-02]
- Send through the marketing stream, not the transactional stream, and expose topic/frequency controls where practical. [BRAZE-TRANS-01][BRAZE-STRAT-01]

## How
- Define one issue-level objective, one primary CTA, and a small number of supporting links; do not turn every issue into an undifferentiated link dump. [BRAZE-STRAT-01][MC-NEWS-01]
- Segment by role, interests, lifecycle stage, location, or prior behavior so each version is useful to its recipients. [MC-SEG-01][BRAZE-STRAT-01]
- Use a recognizable sender, a descriptive subject, a clear header, short sections, hierarchy, headings, and concise paragraphs that can be scanned on mobile. [MC-SUBJ-01][MC-NEWS-01][MC-NEWS-02][LIT-MOBILE-01]
- Keep the editorial promise made at signup, and state or reinforce the expected topic and frequency. [ICO-02][MC-PERM-01]
- Choose send time from recipient data or a timing test rather than a generic industry timetable. [MC-TIME-01][MC-AB-01]
- Track link-level clicks, downstream conversions, unsubscribe/complaint rate, and content-module performance; treat opens only as a directional diagnostic. [MC-REPORT-01][MC-GA-01][LIT-MPP-01]
- Test one element at a time, such as subject framing, content order, CTA wording, or send time. [MC-AB-01]

## Do / Don't quick reference
**Do**
- Keep the topic and cadence promised at signup. [ICO-02][MC-PERM-01]
- Give each issue one objective and one primary CTA. [BRAZE-STRAT-01][MC-NEWS-01]
- Structure short, scannable sections with headings that read well on mobile. [MC-NEWS-02][LIT-MOBILE-01]
- Segment by role, interest, lifecycle, or behavior so each version is useful. [MC-SEG-01][BRAZE-STRAT-01]
- Choose send time from recipient data or a controlled test. [MC-TIME-01][MC-AB-01]

**Don't**
- Don't turn issues into an undifferentiated link dump. [MC-NEWS-01]
- Don't route the newsletter through the transactional stream. [BRAZE-TRANS-01]
- Don't change topic or frequency beyond what the subscriber agreed to. [ICO-02][MC-PERM-01]
- Don't judge issue performance on opens alone. [LIT-MPP-01][MC-REPORT-01]
- Don't use a clickbait or misleading subject line. [FTC-01][MC-SUBJ-01]

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
