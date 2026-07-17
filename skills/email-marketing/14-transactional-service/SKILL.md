---
name: 14-transactional-service
description: Create essential event-triggered messages such as verification, password reset, receipt, shipping, account, security, and service-status emails.
version: 1.0.0
last_reviewed: 2026-07-16
---

# Transactional and Service Email

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`).

## What and why
A transactional email delivers essential information tied to a user action, purchase, account, security event, or service relationship rather than a marketing conversion. [BRAZE-TRANS-01][MC-PERM-01]

## When and where
- Trigger immediately from the authoritative system event and send only to the affected recipient. [BRAZE-TRIG-01][BRAZE-TRANS-01]
- Use a dedicated transactional stream and template so essential information is not delayed or obscured by promotional content; where infrastructure permits, separate transactional and marketing traffic for independent reputation control. [BRAZE-TRANS-01][AWS-SES-SEP-01]

## How
- Put the essential fact and required action first: what happened, item/account, amount or status, timestamp, next step, support path, and security guidance where relevant. [BRAZE-TRANS-01]
- Keep the subject and sender accurate and recognizable, and never disguise marketing as a receipt, security alert, or reply. [FTC-01]
- Keep pure transactional messages free of marketing content; if commercial content changes the primary purpose, apply marketing consent and opt-out rules. [BRAZE-TRANS-01][FTC-01]
- Validate all dynamic data, prevent raw merge-tag exposure, and test links and rendering before deployment. [LIT-QA-01][LIT-TEST-01]
- Monitor delivery success, latency, bounces, authentication, support contacts, completion of the required action, and failure/retry paths. [GMAIL-03][MC-REPORT-01][AWS-SES-MON-01]

## Do / Don't quick reference
**Do**
- Trigger immediately from the authoritative system event, only to the affected recipient. [BRAZE-TRIG-01][BRAZE-TRANS-01]
- Put the essential fact and required action first. [BRAZE-TRANS-01]
- Separate transactional and marketing traffic for independent reputation where infrastructure permits. [BRAZE-TRANS-01][AWS-SES-SEP-01]
- Monitor delivery success, latency, bounces, and authentication continuously. [GMAIL-03][AWS-SES-MON-01]

**Don't**
- Don't disguise marketing as a receipt, security alert, or reply. [FTC-01]
- Don't add commercial content that changes the primary purpose without applying marketing consent and opt-out rules. [BRAZE-TRANS-01][FTC-01]
- Don't ship unvalidated dynamic data or raw merge tags. [LIT-QA-01]
- Don't queue essential messages behind marketing volume. [BRAZE-TRANS-01][AWS-SES-SEP-01]

## Examples
- Password reset: trigger only from a verified reset request tied to the account, send only to the address of record, state the required action and expiry, and never bundle product or promotional content. [BRAZE-TRIG-01][BRAZE-TRANS-01]
- Order receipt: trigger from the confirmed order/payment event, show amount, item, and status with no marketing cross-sell content added to the primary purpose. [BRAZE-TRANS-01][FTC-01]
- Security alert (new sign-in, password changed): trigger from the authoritative security event, send only to the affected account, and treat any delay as a monitoring failure requiring investigation, not a scheduling choice. [BRAZE-TRIG-01][AWS-SES-MON-01][GMAIL-03]

## Mandatory output
Return all of the following:
1. Event and trigger authority: source system, event type/ID, and the authoritative event that justifies this send. [BRAZE-TRIG-01][BRAZE-TRANS-01]
2. Recipient binding: confirmation the message goes only to the account/address tied to the triggering event, with no list or segment substituted. [BRAZE-TRANS-01]
3. Stream and template: confirmation of the transactional stream/template, kept separate from marketing sending infrastructure. [BRAZE-TRANS-01][AWS-SES-SEP-01]
4. Content outline: essential fact, item/account, amount or status, timestamp, required action, support path, and security guidance where relevant, with confirmation no promotional or marketing content is present. [BRAZE-TRANS-01][FTC-01]
5. Delivery and monitoring plan: expected latency and the metrics to track (delivery, bounce, delivery delay, authentication, completion of the required action). [GMAIL-03][AWS-SES-MON-01][MC-REPORT-01]
6. Pre-send QA checklist covering dynamic-data validation, rendering, plain-text fallback, and link checks, followed by a final `SEND`, `HOLD`, or `BLOCK` decision based on trigger authority, recipient accuracy, and delivery readiness. [LIT-QA-01][LIT-TEST-01][AWS-SES-FORMAT-01]
7. A source list containing every citation ID used.

## Agent restrictions
- Never send without a verified, authoritative trigger event bound to the specific recipient; never infer or fabricate an event to justify a send. [BRAZE-TRIG-01][BRAZE-TRANS-01]
- Never expand delivery beyond the account/address bound to the triggering event, and never substitute a marketing list or segment for the affected recipient. [BRAZE-TRANS-01]
- Never add promotional content, discounts, cross-sell, or a marketing call to action that changes the message's primary purpose; if commercial content is required, apply the marketing consent and opt-out rules instead. [BRAZE-TRANS-01][FTC-01]
- Never disguise a marketing message as a receipt, security alert, password reset, or reply notification. [FTC-01][BRAZE-TRANS-01]
- Never delay or queue an essential message behind marketing volume, and never route it through non-transactional infrastructure. [BRAZE-TRANS-01][AWS-SES-SEP-01]
- Never ship unvalidated dynamic data, raw merge tags, or unverified links, especially in messages carrying account, financial, or security detail. [LIT-QA-01][LIT-TEST-01]
- Never base a `SEND` decision on marketing metrics such as opens, clicks, or conversions; base it on trigger authority, recipient accuracy, and delivery/monitoring readiness. [AWS-SES-MON-01][GMAIL-03][BRAZE-TRANS-01]
