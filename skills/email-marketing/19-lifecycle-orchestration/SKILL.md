---
name: 19-lifecycle-orchestration
description: Resolve contact-level collisions across lifecycle flows with deterministic ownership, frequency, suppression, holdout, calendar, and monitoring rules.
version: 1.0.0
last_reviewed: 2026-07-16
---

# Lifecycle Orchestration and Frequency Governance

Use this skill after applying the `00-email-marketing-guardrails` skill (`../00-email-marketing-guardrails/SKILL.md`) whenever a contact can qualify for more than one campaign or channel.

## What and why
A lifecycle orchestrator evaluates all eligible messages together so current customer state, permission, preferences, and campaign pressure produce one auditable contact-level decision rather than several independently valid sends. [BRAZE-STRAT-01][HUB-WF-01]

## Required inputs
- Collect the contact ID, timezone, jurisdiction, consent and suppression state by channel and purpose, channel preferences, segment memberships, lifecycle state, authoritative events, active flow memberships, reserved and completed sends, purchase history, holdout assignments, and configured quiet periods and caps; return `HOLD` rather than inventing missing values. [ICO-02][BRAZE-STRAT-01][HUB-WF-01]
- Collect every candidate's message class, purpose, channel, flow and step ID, business-owned semantic `message_slot`, trigger event and timestamp, subject entity such as cart/order/product, expiry, exit conditions, deduplication key, and experiment ID. [BRAZE-TRANS-01][BRAZE-TRIG-01][HUB-WF-01]
- Define numeric global and segment caps from documented business policy and recipient expectations; do not present one universal cadence as correct for every audience. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]

## Contact-level decision order
Evaluate each contact at reservation time and again immediately before send, recording the input snapshot, winning candidate, rejected candidates, reason codes, next eligible time, and policy version. [HUB-WF-01][BRAZE-STRAT-01]

1. Classify every candidate by primary purpose as essential service, marketing, or mixed; treat mixed messages as marketing and never relabel a promotion to win priority. [BRAZE-TRANS-01][FTC-01]
2. Apply recipient identity and binding, authoritative-event, authentication, bounce, and factual hard gates to every candidate; a failed universal gate is `BLOCK`, not a lower-priority send. [BRAZE-TRANS-01][BRAZE-TRIG-01][GMAIL-01]
3. Apply legal basis, consent, unsubscribe, complaint, and purpose/channel suppression gates to marketing and mixed candidates; block the affected marketing candidate without blocking a separately verified essential-service candidate. [ICO-02][GMAIL-01][BRAZE-TRANS-01]
4. Remove candidates invalidated by a newer authoritative event, an exit condition, loss of ownership, recent purchase, canonical deduplication, or a relevant experiment holdout. [BRAZE-TRIG-01][HUB-WF-01][KL-BROWSE-01][KL-HOLDOUT-01]
5. For remaining marketing candidates, enforce the contact's channel preference, quiet period, and the global and every applicable segment cap; the most restrictive applicable rule wins. [ICO-02][BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
6. Select at most one marketing candidate for the decision window using the declared ownership and precedence rules below; reschedule only while its trigger remains valid and its expiry and exit conditions permit, otherwise drop it. [HUB-WF-01][BRAZE-TRIG-01]
7. When event-bound service information is verified, essential service messages bypass marketing scheduling, quiet periods, and marketing caps; they must never carry marketing content or reset, evade, or consume marketing caps. [BRAZE-TRANS-01][FTC-01]

## Event precedence and ownership
- Let the newest authoritative event update state before campaign priority is considered: purchase exits cart, browse, and incompatible promotion candidates; checkout exits browse; registration exits invitation; renewal exits renewal reminders; opt-out or complaint exits all affected marketing. [HUB-WF-01][KL-CART-01][KL-BROWSE-01][GMAIL-01]
- Acquire one owning flow with an atomic compare-and-set or transaction keyed by contact, objective, and subject entity, and persist its entry event, entry time, current step, exit conditions, and ownership expiry; exactly one concurrent worker proceeds and each loser records `DROP: OWNERSHIP_CONFLICT`. [HUB-WF-01][BRAZE-TRIG-01]
- Resolve remaining marketing conflicts only with a published, business-owned precedence table based on current intent and message expiry, not whichever automation runs first; return `HOLD: PRECEDENCE_POLICY_MISSING` when no applicable table exists. [BRAZE-TRIG-01][BRAZE-STRAT-01]
- Break equal-priority ties by earliest real expiry, then most recent specific trigger, then oldest reservation request; log the tie-break and never invent urgency. [FTC-01][BRAZE-TRIG-01]
- Release ownership immediately when the goal completes, the trigger expires, the contact becomes ineligible, or the contact opts out or complains; re-entry requires a new qualifying event and the flow's re-entry rule. [HUB-WF-01][GMAIL-01]

## Pressure, suppression, and experiments
- In one atomic transaction, validate and reserve ownership and canonical deduplication, count and reserve every applicable global and segment pressure window, and write one exclusive winner slot keyed by contact and decision window; an exhausted cap returns `DEFER: CAP_REACHED`, otherwise a candidate finding that winner slot returns `DEFER: DECISION_WINDOW_TAKEN`, and every failed transaction rolls back all reservations. [HUB-WF-01][BRAZE-TRIG-01][BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
- Apply the recipient's permitted channels and stated topic/frequency choices first, choose only an allowed channel, and do not substitute email, SMS, push, or another channel without permission for that channel and purpose. [ICO-02][BRAZE-STRAT-01]
- Defer non-urgent marketing to the first eligible local time after the quiet period only if the trigger remains valid; when timezone is unknown, use the documented conservative fallback or return `HOLD`. [BRAZE-STRAT-01][HUB-WF-01]
- Build the versioned canonical deduplication key as `v2|contact_id|purpose|event_type|event_id|entity_type|entity_id|message_slot`, using normalized authoritative event and entity IDs together and the literal `none` only when a field is not applicable; define `message_slot` as a business-owned semantic identity such as `cart-reminder-1`, never a provider flow, step, template, or channel ID, so equivalent messages collide across implementations and channels while a legitimate later sequence slot remains distinct; atomically reserve the key in the winner transaction and return `DROP: DUPLICATE` for a matching reservation or send in its validity window. [BRAZE-TRIG-01][HUB-WF-01]
- Define recent-purchase suppression by product/category, campaign purpose, and a documented lookback window; suppress stale acquisition, browse, cart, price, or incompatible recommendation messages while preserving relevant service and post-purchase information. [KL-BROWSE-01][KL-LOWSTOCK-01][KL-XSELL-01][BRAZE-TRANS-01]
- Before a coordinated experiment starts, persist its experiment ID, contact randomization unit, sampled control membership, variant, eligibility snapshot, named campaign/flow scope, and start/end; keep that assignment unchanged through the test, exclude control members from every marketing treatment in scope across channels, and preserve essential-service eligibility. [KL-HOLDOUT-01][BRAZE-TRANS-01]

## Behavioral acceptance traces
Each implementation must reproduce these decision-table outcomes before launch. [HUB-WF-01][BRAZE-TRIG-01]

| Case | Input trace | Required outcome |
|---|---|---|
| Marketing opt-out with verified receipt | Marketing candidate is unsubscribed; a separately verified order receipt is eligible. | `BLOCK: UNSUBSCRIBED` for marketing and `SEND` for the receipt; the marketing block does not block essential service. [ICO-02][BRAZE-TRANS-01] |
| Concurrent ownership | Two workers request the same contact, objective, and entity with no existing owner. | One atomic acquisition wins; exactly one worker proceeds and the loser records `DROP: OWNERSHIP_CONFLICT`. [HUB-WF-01][BRAZE-TRIG-01] |
| Concurrent cap boundary | Two distinct candidates and deduplication keys observe one remaining pressure slot. | One atomic transaction selects one winner; the other records `DEFER: CAP_REACHED`, so reserved plus sent never exceeds the cap. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01] |
| Concurrent decision window with cap headroom | With cap 5 and pressure 0, two workers submit distinct eligible objectives, events, entities, and deduplication keys for the same contact and decision window. | One transaction writes the exclusive winner slot; the other records `DEFER: DECISION_WINDOW_TAKEN` even though four cap slots remain. [HUB-WF-01][BRAZE-STRAT-01] |
| Cross-flow and cross-channel duplicate | Different flows or channels produce the same semantic `message_slot` for the same contact, purpose, authoritative event, and entity. | All derive the same canonical key; one reservation wins and every other candidate records `DROP: DUPLICATE`. [BRAZE-TRIG-01][HUB-WF-01] |
| Legitimate next sequence step | `cart-reminder-1` was sent and the same contact, purpose, event, and entity later qualify for documented `cart-reminder-2`. | The semantic `message_slot` produces a distinct canonical key, so deduplication leaves step 2 eligible for the remaining policy gates. [BRAZE-TRIG-01][HUB-WF-01] |
| Purchase after cart | A purchase event arrives after a cart candidate for the same order or cart. | State updates first and the cart candidate records `DROP: RECENT_PURCHASE`; relevant receipt or post-purchase service remains eligible. [KL-CART-01][KL-BROWSE-01][BRAZE-TRANS-01] |
| Control leakage and service exception | A stored control member qualifies for two covered marketing flows and a verified receipt during the test window. | Both marketing candidates record `DROP: HOLDOUT`; the receipt remains eligible and no channel change bypasses the holdout. [KL-HOLDOUT-01][BRAZE-TRANS-01] |
| Service-label abuse | Promotional content is labeled transactional or urgent. | Primary-purpose classification makes it marketing or mixed and `BLOCK`s any attempt to bypass consent, caps, deduplication, or holdout rules. [BRAZE-TRANS-01][FTC-01] |
| Missing precedence policy | Two otherwise eligible marketing candidates conflict and no applicable business-owned precedence table exists. | Policy readiness is `HOLD: PRECEDENCE_POLICY_MISSING`; neither candidate is selected by an invented default. [BRAZE-TRIG-01][BRAZE-STRAT-01] |

## Mandatory output
Return all of the following:

1. Policy header: policy version, evaluation timestamp, decision window, timezone fallback, configured global/segment caps, quiet periods, channel-preference source, and data freshness. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
2. Contact-level decision table: contact, candidate, class, authoritative event, owner, eligibility, pressure counts, holdout, deduplication result, decision (`SEND`, `DEFER`, `DROP`, or `BLOCK`), reason code, and next eligible time. [HUB-WF-01][BRAZE-TRANS-01]
3. Conflict matrix: each flow pair, governing event precedence, owner, tie-break, exit/re-entry rule, recent-purchase rule, and whether the loser is deferred or dropped. [HUB-WF-01][BRAZE-TRIG-01]
4. Campaign calendar: date/time and timezone, campaign/flow, segment, channel, expected eligible volume, cap budget, holdout, owner, dependencies, and collision notes. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
5. Monitoring and exception report: sends/reservations by contact and flow, cap and quiet-period blocks, collisions won/lost, duplicate attempts, stale-event drops, purchase suppressions, holdout leakage, service latency, delivery/bounce/complaint metrics, and alerts with owners. [AWS-SES-MON-01][GMAIL-03][BRAZE-METRIC-01]
6. One worked contact trace showing the ordered input snapshot, every rejected candidate and reason code, the winning decision, and the next reevaluation trigger. [HUB-WF-01][BRAZE-TRIG-01]
7. A final `SEND`, `HOLD`, or `BLOCK` decision for policy readiness, including the blocking or hold reason when not send-ready, and a source list containing every citation ID used. [LIT-QA-01][GMAIL-01]

## Agent restrictions
- Never invent consent, caps, quiet hours, preferences, event timestamps, ownership, purchase windows, or holdout assignments; unresolved hard-gate data is `BLOCK` and unresolved operational policy is `HOLD`. [ICO-02][GMAIL-01][BRAZE-STRAT-01]
- Never let campaign-level settings loosen a global or recipient-specific restriction, and never evaluate flows independently when their decision windows overlap. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
- Never use an essential-service label, transactional stream, or urgent priority to carry promotion or bypass marketing consent, suppression, preferences, caps, quiet periods, deduplication, or holdouts. [BRAZE-TRANS-01][FTC-01]
- Never withhold, delay behind marketing, or include essential service messages in marketing experiments or cap counts; monitor their latency and delivery separately. [BRAZE-TRANS-01][AWS-SES-SEP-01][AWS-SES-MON-01]
