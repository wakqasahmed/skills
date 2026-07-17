---
name: 20-list-growth-signup-preferences
description: Design permission-first email signup forms, consent records, double opt-in flows, lead-magnet capture, preference centers, and verified welcome handoffs.
version: 1.0.0
last_reviewed: 2026-07-16
---

# List Growth, Signup Consent, and Preferences

Use this skill only after applying `00-email-marketing-guardrails` (`../00-email-marketing-guardrails/SKILL.md`) to design or review first-party subscriber capture before campaign drafting, and treat it as operational guidance rather than legal advice. [ICO-01][ICO-02][MC-LISTS-01]

## Consent-capture contract
- Apply `00-email-marketing-guardrails` first and run `18-jurisdiction-compliance-routing` before publishing a form; return `HOLD` while required routing facts are collectible and `BLOCK` when the applicable basis or capture requirement cannot be verified. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]
- Persist the contact identifier, signup source and form ID, exact consent statement and form version, timestamp, jurisdiction facts, channel, purpose, selected preferences, capture method, confirmation state, and later withdrawals or changes; do not reduce the audit trail to a generic consent flag. [ICO-CONSENT-01][KL-CONSENT-01][MC-PROFILE-01]
- Name the sender, channel, content or purpose, and expected frequency at capture, link the applicable privacy information, and use separate unbundled choices where purposes or channels differ. [ICO-02][ICO-04][KL-FORMS-01]
- Use an unchecked affirmative control when the selected jurisdiction route requires consent, keep optional marketing separate from terms or resource delivery, and retain the exact copy shown with its policy/form version. [ICO-CONSENT-01][ICO-02][MC-GDPR-01]
- Collect only fields that support the stated signup, preference, routing, or personalization purpose, and explain why optional information is requested. [ICO-CONSENT-01][MC-GDPR-01]
- Use confirmation or double opt-in when stronger address ownership and intent verification is appropriate; do not treat an unconfirmed grant as subscribed. [KL-DOI-01][MC-DOI-01]

## Double opt-in and welcome handoff
- Choose single or double opt-in from the applicable jurisdiction route, risk, list-quality needs, and documented business policy; double opt-in is a strong verification practice, not a universal legal requirement. [MC-DOI-01][KL-DOI-01][ICO-01]
- Prefer double opt-in when fake signups, mistyped addresses, weak source assurance, or proof-of-intent risk outweigh the extra confirmation step. [KL-DOI-01][MC-DOI-01]
- For double opt-in, key `PENDING_CONFIRMATION` to the contact, list, channel, and purpose after form submission; send only the confirmation message for that pending grant and move that grant to `SUBSCRIBED` only after confirmation. An expired or absent confirmation keeps marketing under that grant ineligible without suppressing unrelated eligible service or a separately verified permission. [MC-DOI-01][KL-DOI-01]
- Keep confirmation copy limited to the requested verification, identify the sender and requested channel, and provide a clear confirm action without unrelated promotion. [MC-DOI-01][FTC-01]
- Hand a `SUBSCRIBED` grant and its source, statement version, confirmation timestamp, jurisdiction, list, channel, purpose, and preferences to `02-welcome-onboarding`; trigger welcome only for the same list, channel, and purpose, never from the matching `PENDING_CONFIRMATION` grant. [KL-DOI-01][KL-WELCOME-01][ICO-CONSENT-01]

## Preferences and lead magnets
- Offer meaningful topic, channel, and frequency choices, preserve a clear unsubscribe-all option, apply changes to future eligibility and orchestration, and record the changed values and timestamp without overwriting the prior audit trail. [BRAZE-STRAT-01][ICO-CONSENT-01]
- Apply `19-lifecycle-orchestration` after a preference change when the contact can qualify for multiple flows or channels, and let the most restrictive current permission or preference govern eligibility. [BRAZE-STRAT-01][ICO-02]
- Describe the promised resource and any marketing subscription separately and truthfully, disclose what follows after signup, and deliver the resource as promised without presenting access as proof of consent to undisclosed marketing. [FTC-01][ICO-02][KL-WELCOME-01]
- If access to a lead magnet is conditional on marketing signup, verify that the selected jurisdiction route and counsel permit that design and that the choice remains valid; otherwise separate resource delivery from marketing permission. [ICO-CONSENT-01][ICO-01]
- Never replace first-party capture with bought, rented, scraped, harvested, publicly copied, or otherwise unverifiable addresses, and never invent conversion claims or unsupported signup tactics. [MC-LISTS-01][ICO-04][FTC-01]

## Behavioral acceptance traces
| Trace | Given | Required outcome |
|---|---|---|
| Incomplete consent record | Signup lacks the statement version or channel. | `HOLD: CONSENT_RECORD_INCOMPLETE`; collect the missing field and do not mark the contact subscribed. [ICO-CONSENT-01][ICO-02] |
| Double opt-in pending | A form submission for a specific list, email channel, and product-news purpose is valid but confirmation has not occurred. | Store that grant as `PENDING_CONFIRMATION`; permit its confirmation message and exclude only matching marketing and welcome. [MC-DOI-01][KL-DOI-01] |
| Cross-purpose confirmation isolation | A contact is pending for a new product-news list while an existing education permission and an order receipt are independently eligible. | The new grant remains pending; the education permission and receipt remain eligible, and confirmation does not grant product-news marketing for another list, channel, or purpose. [MC-DOI-01][KL-DOI-01] |
| Preference change | A subscribed contact changes from weekly product news to monthly education only. | Timestamp the new choices, retain the prior record, update eligibility and orchestration, and exclude weekly product news. [BRAZE-STRAT-01][ICO-CONSENT-01] |
| Lead magnet | A form promises a guide and separately offers clearly described email marketing. | Deliver the guide as promised; subscribe only when the marketing choice and applicable route are valid, with no hidden or bundled permission. [FTC-01][ICO-02][KL-WELCOME-01] |
| Prohibited acquisition | Bought or scraped addresses are offered for a marketing audience. | `BLOCK: UNVERIFIABLE_ACQUISITION`; do not import or send to those addresses. [MC-LISTS-01][ICO-04] |
| Confirmed welcome handoff | A pending grant for the same list, channel, and purpose confirms before expiry. | Record confirmation, set that grant to `SUBSCRIBED`, and pass its complete consent and preference record to `02-welcome-onboarding`. [KL-DOI-01][KL-WELCOME-01][ICO-CONSENT-01] |

## Mandatory output
Return all of the following before publishing or changing capture: [ICO-CONSENT-01][KL-FORMS-01]
1. Signup objective, audience, form placement, sender identity, and promised value. [KL-FORMS-01][FTC-01]
2. Jurisdiction-routing result and the permission or other documented basis required by channel and purpose. [ICO-01][FTC-01][EU-EC-01][CRTC-CASL-01]
3. Field, disclosure, affirmative-action, privacy-link, and consent-statement copy specification. [ICO-02][ICO-04][MC-GDPR-01]
4. Consent-record schema containing source, statement/form version, timestamp, jurisdiction, list, channel, purpose, preferences, method, state, and change history. [ICO-CONSENT-01][KL-CONSENT-01][MC-PROFILE-01]
5. Address validation, bot/abuse protection, single- or double-opt-in decision, grant-scoped pending state, expiry, and retry behavior. [KL-DOI-01][MC-DOI-01]
6. Preference-center choices, unsubscribe-all behavior, and downstream eligibility/orchestration changes. [BRAZE-STRAT-01][ICO-CONSENT-01]
7. Lead-magnet delivery terms and the separate marketing-permission treatment. [FTC-01][ICO-02][KL-WELCOME-01]
8. Confirmed-only handoff contract for `02-welcome-onboarding`, plus a final `SEND`, `HOLD`, or `BLOCK` decision. [KL-DOI-01][KL-WELCOME-01]
9. A source list containing every citation ID used. [ICO-CONSENT-01][KL-FORMS-01][MC-DOI-01]

## Agent restrictions
- Never infer marketing permission from an address, purchase, resource request, or pre-checked control. [ICO-02][ICO-CONSENT-01]
- Never mark a double-opt-in grant subscribed, send marketing under that grant, or trigger its welcome before confirmation; never use confirmation for one list, channel, or purpose to grant another. [MC-DOI-01][KL-DOI-01]
- Never describe double opt-in as universally required by law or single opt-in as universally sufficient. [MC-DOI-01][ICO-01]
- Never conceal marketing consent inside lead-magnet delivery or make unsupported conversion, urgency, scarcity, or performance claims. [FTC-01][ICO-02]
- Never buy, rent, scrape, harvest, or copy public addresses into a marketing audience. [MC-LISTS-01][ICO-04]
