---
name: 02-welcome-onboarding
description: Create a permission-triggered welcome or onboarding sequence that delivers the signup promise and moves a new contact toward activation or first purchase.
version: 1.0.0
last_reviewed: 2026-07-15
---

# Welcome and Onboarding Series

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A welcome series begins immediately after a valid signup and introduces the value, expectations, and next step of the relationship. [KL-WELCOME-01][HUB-CONSENT-01]

## When and where
- Trigger only from a verified signup, account creation, or other documented permission event; keep email and other channel consents separate. [KL-WELCOME-01][ICO-02]
- Use a marketing flow for promotional onboarding and a transactional flow only for essential account-verification or service messages. [BRAZE-TRANS-01][MC-PERM-01]

## How
- Use Klaviyo’s evidence-based baseline of three emails over about one week: immediately, about three days later, then about four days later; test alternatives for the actual audience. [KL-WELCOME-01]
- Deliver any promised incentive or resource in the first message, clearly explain the value proposition, and set expectations for future messages. [KL-WELCOME-01]
- Use later messages for brand story/mission, key products or content, social proof available from verified assets, preference capture, and a clear activation or first-purchase step. [KL-WELCOME-01][BRAZE-STRAT-01]
- Branch by customer vs non-customer, signup source, stated interest, or completed activation event so recipients do not receive irrelevant steps. [KL-WELCOME-01][HUB-WF-01]
- Exit or change the path when the recipient completes the target action, unsubscribes, complains, or becomes ineligible. [HUB-WF-01][GMAIL-01]
- Measure activation, first purchase, time to value, click-to-action rate, unsubscribe/complaint rate, and incremental conversion against a holdout when volume permits. [BRAZE-METRIC-01][KL-SEGTEST-01]

## Do / Don't quick reference
**Do**
- Send the first message immediately after a verified signup or permission event. [KL-WELCOME-01]
- Deliver any promised incentive or resource in the first email. [KL-WELCOME-01]
- Set expectations for future content and frequency. [KL-WELCOME-01][MC-PERM-01]
- Branch customer vs non-customer and by signup source or stated interest. [KL-WELCOME-01][HUB-WF-01]
- Exit the flow when the recipient completes the target action. [HUB-WF-01]

**Don't**
- Don't trigger a welcome without a documented permission event. [ICO-02][KL-WELCOME-01]
- Don't cram everything into one email; Klaviyo's baseline is three emails over about a week. [KL-WELCOME-01]
- Don't keep sending after activation, unsubscribe, or complaint. [HUB-WF-01][GMAIL-01]
- Don't include social proof that is not from verified assets. [FTC-01][KL-WELCOME-01]

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
