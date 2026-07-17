---
name: 21-deliverability-sender-operations
description: Preflight sender authentication (SPF, DKIM, DMARC alignment), list hygiene, bounce/complaint/suppression handling, domain/IP reputation monitoring and recovery, warm-up and volume ramping, and transactional/marketing traffic separation.
version: 1.0.0
last_reviewed: 2026-07-17
---

# Deliverability and Sender Operations

Use this skill only after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`). Apply it independently of any campaign archetype whenever a user requests a deliverability audit, sender-authentication setup, reputation-recovery plan, or incident response, and whenever a campaign-specific skill's guardrail checks cannot be verified.

## What and why
Sender operations determine whether authenticated, well-behaved mail reaches the inbox at all; a campaign can satisfy every consent and creative gate and still fail if authentication, list hygiene, or reputation are broken. [GMAIL-01][YAHOO-01]

## When and where
- Run this skill before onboarding a new sending domain or IP, before any bulk-volume increase, after any spike in bounces or complaints, after a domain/IP reputation or blocklist incident, and on a recurring monitoring cadence. [GMAIL-01][GMAIL-03][AWS-SES-MON-01]
- Run it independently of campaign selection; a user can request a deliverability audit or incident plan without choosing a campaign archetype. [GMAIL-01][AWS-SES-MON-01]
- Treat its output as an operational precondition for every campaign-specific skill: a `HALT` here overrides an otherwise-ready campaign. [GMAIL-01][GMAIL-02]

## How

### Authentication preflight
- Authenticate every sending domain with SPF or DKIM at minimum, and require SPF, DKIM, and DMARC alignment for bulk sending. [GMAIL-01][YAHOO-01]
- Publish the DMARC record as a `_dmarc.<domain>` TXT record with a `p=` policy tag (`none`, `quarantine`, or `reject`), and set up SPF and DKIM before publishing DMARC; a message passes DMARC only when it passes SPF with SPF alignment or DKIM with DKIM alignment. [GOOGLE-DMARC-01]
- Verify TLS support, valid forward and reverse DNS/PTR records, and a stable, aligned visible `From` identity for each sending domain and IP. [GMAIL-01]
- For domains sending more than 5,000 messages per day to Outlook.com/Microsoft mailboxes, verify SPF, DKIM, and DMARC are all in place; unauthenticated mail from qualifying senders is junked and is planned to be rejected. [MS-SNDS-01]
- Treat any domain or IP without verified SPF/DKIM, or without an aligned DMARC record for bulk sending, as authentication-incomplete and not send-ready. [GMAIL-01][YAHOO-01][GOOGLE-DMARC-01]

### List hygiene, bounce, complaint, and suppression handling
- Classify bounces (hard vs soft) and complaints from mailbox-provider feedback loops and delivery events, and suppress hard bounces and complaints immediately. [GMAIL-01][AWS-SES-MON-01]
- Support one-click unsubscribe using the `List-Unsubscribe` header with an HTTPS URI and a `List-Unsubscribe-Post: List-Unsubscribe=One-Click` header so a mailbox provider can unsubscribe a recipient with a single POST and no confirmation page. [GMAIL-01][YAHOO-01][IETF-RFC8058-01]
- Process every unsubscribe, complaint, and hard bounce into suppression, and honor it operationally within 48 hours even where law allows longer. [GMAIL-01][YAHOO-01][MC-SPAM-01]
- Identify never-engaged or persistently inactive contacts, make at most a deliberate final re-engagement attempt, and sunset non-responders out of ongoing sends. [KL-NEVER-01][KL-SUNSET-01]
- Never re-add a suppressed address to a sendable audience without a new, verifiable, unambiguous re-permission event. [GMAIL-01][ICO-03]

### Reputation monitoring and recovery
- Monitor Gmail Postmaster Tools and mailbox-provider diagnostics for spam-rate, authentication, reputation, and delivery-error signals. [GMAIL-03]
- Target a Gmail user-reported spam rate below 0.1% and treat 0.3% or higher as an incident requiring immediate volume and content intervention, never a tolerated steady state. [GMAIL-01][GMAIL-02]
- Monitor sends, deliveries, bounces, complaints, rejects, and delivery delays through provider-level event publishing and metrics (for example, Amazon SES configuration-set event destinations). [AWS-SES-MON-01]
- When reputation is degraded (elevated spam rate, blocklist listing, or a mailbox-provider throttling/blocking signal), reduce volume, isolate the affected stream, and only resume sending through a staged recovery ramp; never resume full volume immediately after a reputation incident. [GMAIL-01][BRAZE-HOLIDAY-01]

### Warm-up and volume ramping
- Warm up every new sending domain or dedicated IP gradually before using it at full capacity; reputation-building time varies by mailbox provider, and a new address with little or no sending history is more likely to be junked or blocked. [AWS-SES-WARM-01]
- Prefer automatic warm-up where available; Amazon SES's automatic dedicated-IP warm-up increases sending volume on a predefined, time-based plan over 45 days, independent of actual sending volume. [AWS-SES-WARM-01]
- During warm-up, send to the most engaged/active recipients first to keep the complaint rate low, and reduce volume in response to elevated bounce, block, or throttle signals rather than pushing through them. [AWS-SES-WARM-01]
- After warm-up completes, continue increasing volume gradually toward the target instead of an immediate jump; a large, sudden increase from a given address can trigger blocking or throttling from a mailbox provider. [AWS-SES-WARM-01][BRAZE-HOLIDAY-01]

### Traffic separation
- Separate transactional and marketing sending infrastructure (for example, distinct configuration sets or dedicated IP pools) so one stream's reputation does not depend on the other's volume or complaint behavior. [AWS-SES-SEP-01][BRAZE-TRANS-01]
- Confirm essential transactional/service mail is never queued behind or throttled by marketing volume, and that a marketing-side incident cannot delay a transactional stream. [AWS-SES-SEP-01][BRAZE-TRANS-01]

## Do / Don't quick reference
**Do**
- Authenticate every sending domain with SPF and DKIM, and require aligned DMARC for bulk sending. [GMAIL-01][YAHOO-01][GOOGLE-DMARC-01]
- Support one-click unsubscribe and process unsubscribes, complaints, and hard bounces into suppression within 48 hours. [GMAIL-01][YAHOO-01][IETF-RFC8058-01][MC-SPAM-01]
- Monitor Postmaster Tools, provider feedback loops, and event/metric data continuously. [GMAIL-03][AWS-SES-MON-01]
- Warm up new domains and dedicated IPs gradually, and ramp recovery volume gradually after any reputation incident. [AWS-SES-WARM-01][BRAZE-HOLIDAY-01]
- Keep transactional and marketing traffic on separated infrastructure. [AWS-SES-SEP-01][BRAZE-TRANS-01]

**Don't**
- Don't run bulk sending without SPF, DKIM, and aligned DMARC. [GMAIL-01][YAHOO-01][GOOGLE-DMARC-01]
- Don't let the spam-complaint rate reach or remain at 0.3%; treat it as an incident, not a metric to average out. [GMAIL-02]
- Don't leave a bounced, complained, or unsubscribed contact eligible for further marketing sends. [GMAIL-01][ICO-03]
- Don't resume full sending volume immediately after a new IP/domain launch or a reputation incident; ramp gradually instead. [AWS-SES-WARM-01][BRAZE-HOLIDAY-01]
- Don't share transactional and marketing sending infrastructure when separation is available. [AWS-SES-SEP-01][BRAZE-TRANS-01]

## Behavioral acceptance traces
| Trace | Given | Required outcome |
|---|---|---|
| Missing DMARC alignment | A bulk-sending domain has valid SPF and DKIM but no aligned DMARC record. | `HOLD: AUTH_ALIGNMENT_INCOMPLETE`; publish the `_dmarc` record and verify alignment before resuming bulk sending. [GOOGLE-DMARC-01][GMAIL-01] |
| Spam-rate breach | Gmail Postmaster Tools reports a spam rate at or above 0.3%. | `HALT: SPAM_RATE_BREACH`; reduce volume and isolate the affected stream immediately. [GMAIL-01][GMAIL-02] |
| Reputation recovery | A domain/IP is recovering from a blocklist or throttling incident. | `RECOVER: STAGED_RAMP`; resume sending on a staged volume ramp to the most engaged recipients first, never at full prior volume immediately. [AWS-SES-WARM-01][BRAZE-HOLIDAY-01] |
| Unwarmed new IP at full volume | A newly provisioned dedicated IP with no sending history is requested at full target volume on day one. | `BLOCK: WARMUP_REQUIRED`; require a gradual warm-up plan before any full-volume send. [AWS-SES-WARM-01] |
| Suppression sync failure | A contact who unsubscribed or complained is still present in an eligible send audience. | `BLOCK: SUPPRESSION_SYNC_FAILURE`; do not send until the suppression list is confirmed synchronized. [GMAIL-01][ICO-03] |
| Never-engaged accumulation | A segment of contacts has not opened or clicked across an extended, documented period and has received no sunset treatment. | `HOLD: LIST_HYGIENE_STALE`; run a final re-engagement attempt, then suppress non-responders. [KL-NEVER-01][KL-SUNSET-01] |
| Traffic separation missing | Transactional and marketing mail share the same sending domain/IP pool with no configuration-set or pool separation. | `HOLD: TRAFFIC_SEPARATION_MISSING`; separate the streams before scaling marketing volume. [AWS-SES-SEP-01][BRAZE-TRANS-01] |
| All gates pass | Authentication, suppression sync, complaint rate, warm-up status, and traffic separation are all verified current. | `READY`; proceed with the requested sending plan under continued monitoring. [GMAIL-03][AWS-SES-MON-01] |

## Mandatory output
Return all of the following:
1. Authentication audit result: SPF/DKIM presence and DMARC alignment status per sending domain, with the record source checked. [GMAIL-01][YAHOO-01][GOOGLE-DMARC-01]
2. List-hygiene state: bounce/complaint categorization, suppression coverage, and never-engaged/sunset status. [GMAIL-01][KL-NEVER-01][KL-SUNSET-01]
3. Complaint-rate and reputation readout: current spam rate against the 0.1%/0.3% thresholds, Postmaster Tools findings, and any blocklist/throttling signal. [GMAIL-02][GMAIL-03]
4. Suppression-list integrity confirmation: verification that no bounced, complained, or unsubscribed contact remains in the eligible audience. [GMAIL-01][ICO-03]
5. Warm-up/ramp or recovery plan when applicable: staged volume schedule, most-engaged-first targeting, and the trigger conditions that would pause or slow the ramp. [AWS-SES-WARM-01][BRAZE-HOLIDAY-01]
6. Traffic-separation confirmation: transactional and marketing streams verified on separated sending infrastructure. [AWS-SES-SEP-01][BRAZE-TRANS-01]
7. Monitoring plan: which signals are tracked (Postmaster Tools, provider feedback loops, delivery/bounce/complaint events), at what cadence, and the owner who acts on an alert. [GMAIL-03][AWS-SES-MON-01]
8. Final `READY`, `RECOVER`, `HOLD`, `BLOCK`, or `HALT` decision based on the evidence above. [GMAIL-01][GMAIL-02]
9. A source list containing every citation ID used.

## Agent restrictions
- Never issue `READY` when SPF/DKIM/DMARC alignment, suppression-list integrity, or current complaint-rate evidence is missing or unverified. [GMAIL-01][GMAIL-02][GOOGLE-DMARC-01]
- Never resume full sending volume immediately after a new domain/IP launch or a reputation incident; require a staged ramp instead. [AWS-SES-WARM-01][BRAZE-HOLIDAY-01]
- Never leave a bounced, complained, or unsubscribed contact eligible for further marketing sends, and never treat a suppression-sync gap as acceptable. [GMAIL-01][ICO-03]
- Never let the spam-complaint rate reach or remain at 0.3%; treat it as an incident requiring immediate intervention, not an average to tolerate. [GMAIL-02]
- Never mix transactional and marketing traffic on shared sending infrastructure when configuration-set or IP-pool separation is available. [AWS-SES-SEP-01][BRAZE-TRANS-01]
- Never present a `HOLD` or `HALT` deliverability result as a green light for campaign-specific drafting or sending. [GMAIL-01][GMAIL-02]
