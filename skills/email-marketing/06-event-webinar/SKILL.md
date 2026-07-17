---
name: 06-event-webinar
description: Create invitation, registration, reminder, and follow-up emails for physical or virtual events.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Event and Webinar Campaign

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
An event campaign moves an eligible audience from invitation to registration, attendance, and a useful post-event next step. [MC-EVENT-01][HUB-EVENT-01]

## When and where
- Use distinct paths for invitees, registrants, attendees, no-shows, speakers, and customers when their information or next action differs. [HUB-EVENT-01]
- Treat a registration confirmation and access link as service information; keep optional promotional follow-up subject to marketing permission. [BRAZE-TRANS-01][ICO-02]

## How
- Make the invitation explain the audience value, topic, speaker, date, time zone, duration, format, price, location or join method, and registration CTA. [MC-EVENT-02]
- Use a reminder baseline around two weeks, one week, and one day before the event when the lead time allows, then test the cadence for the audience. [MC-EVENT-01]
- Include essential logistics, access instructions, troubleshooting guidance, and a concise mobile-friendly layout in reminders. [MC-EVENT-01][MC-EVENT-02]
- Provide both Google Calendar and ICS options where possible. [HUB-CAL-01]
- Stop invitation emails after registration and stop reminders after cancellation or ineligibility. [HUB-WF-01]
- After the event, segment attendees and no-shows; send the recording or resources and one clear next-step CTA. [HUB-EVENT-01][ZOOM-EVENT-01]
- Measure registration conversion, attendance/show rate, engagement, qualified follow-up actions, pipeline or revenue, unsubscribes, and complaints. [BRAZE-METRIC-01][HUB-B2B-01]

## Do / Don't quick reference
**Do**
- State the audience value, topic, speaker, date, time zone, duration, format, and registration CTA in the invitation. [MC-EVENT-02]
- Use a reminder baseline of about two weeks, one week, and one day before, then test. [MC-EVENT-01]
- Offer both Google Calendar and ICS options. [HUB-CAL-01]
- Include join logistics, access instructions, and troubleshooting in reminders. [MC-EVENT-01][MC-EVENT-02]
- Segment attendees and no-shows for distinct follow-up with the recording and one next step. [HUB-EVENT-01][ZOOM-EVENT-01]

**Don't**
- Don't keep inviting people who already registered. [HUB-WF-01]
- Don't add promotional follow-up to service confirmations without marketing permission. [BRAZE-TRANS-01][ICO-02]
- Don't bury the join method or time-zone information. [MC-EVENT-01][MC-EVENT-02]
- Don't send reminders after cancellation or ineligibility. [HUB-WF-01]

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
