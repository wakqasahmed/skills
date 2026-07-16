---
name: 00-email-marketing-guardrails
description: Mandatory consent, identity, authentication, deliverability, audience, creative, measurement, and QA gates for any email campaign work. Apply this skill first, before any campaign-specific email marketing skill, when planning, drafting, reviewing, or approving email sends.
version: 1.0.0
last_reviewed: 2026-07-16
---

# Global Email Marketing Guardrails

Apply these gates before every campaign-specific `SKILL.md`. A campaign that fails a hard gate must be marked `BLOCK`, not drafted as send-ready.

## 1. Classification and permission gate
- Classify each message as marketing/promotional, transactional/service, or mixed based on its primary purpose; do not disguise marketing as a service message. [BRAZE-TRANS-01][FTC-01]
- Record the address source, signup statement, permitted channels/purposes, timestamp where available, jurisdiction, and current suppression status. [ICO-02][ICO-04][HUB-CONSENT-01]
- Before drafting recipient-facing content, apply `18-jurisdiction-compliance-routing` when a recipient is in the US, UK, EEA, or Canada; the sender or sending system is in Canada; or a jurisdiction is unknown or conflicting. Unresolved routing is `HOLD` or `BLOCK`, not send-ready copy. [FTC-01][ICO-01][EU-EC-01][CRTC-CASL-01]
- For marketing, require a valid permission or other documented lawful basis applicable to the recipient and jurisdiction; a provided email address is not automatically consent for every marketing purpose. [ICO-01][ICO-02][ICO-03]
- Never use bought, scraped, harvested, or unverifiable lists. [MC-LISTS-01][ICO-04]
- Keep email, SMS, push, and other channel consent separate. [ICO-02]

## 2. Identity, content, and opt-out gate
- Use accurate `From`, `Reply-To`, domain, routing, and subject information, and identify the sender/business clearly. [FTC-01]
- Ensure the subject and preview accurately represent the message; do not create false urgency, scarcity, reply/forward history, account alerts, or relationship claims. [FTC-01][MC-SUBJ-01]
- Include the legally required business identity/address and a clear unsubscribe mechanism in commercial mail. [FTC-01]
- Make unsubscribe easy to find, support one-click unsubscribe where required by mailbox-provider rules, and process it operationally within 48 hours even where law allows longer. [GMAIL-01][YAHOO-01][MC-SPAM-01]
- Maintain suppression for unsubscribes, complaints, hard bounces, and jurisdiction-specific do-not-contact requests. [GMAIL-01][ICO-03]

## 3. Authentication and deliverability gate
- Authenticate all sending domains; use SPF or DKIM for all senders and SPF, DKIM, and DMARC alignment for bulk sending as required by Gmail/Yahoo guidance. [GMAIL-01][YAHOO-01]
- Use TLS, valid forward/reverse DNS/PTR where applicable, aligned visible From identity, and a stable sending infrastructure. [GMAIL-01]
- Monitor Gmail Postmaster Tools and provider diagnostics for spam, reputation, authentication, and delivery errors. [GMAIL-03]
- Target Gmail user-reported spam below 0.1% and never allow it to reach or remain at 0.3% or higher. [GMAIL-01][GMAIL-02]
- Warm or increase volume gradually; do not suddenly expand frequency or include long-inactive audiences without staged monitoring. [GMAIL-01][BRAZE-HOLIDAY-01]

## 4. Audience and frequency gate
- Define eligibility and explicit exclusions before writing copy, including consent, lifecycle stage, geography, product availability, purchase status, and overlapping flow membership. [BRAZE-STRAT-01][HUB-WF-01]
- Segment from reliable first-party behavior, preferences, lifecycle, and purchase data so content is relevant. [MC-SEG-01][BRAZE-STRAT-01]
- Apply frequency caps, preference-center choices, quiet periods where appropriate, and conflict rules between campaigns. [BRAZE-STRAT-01][BRAZE-HOLIDAY-01]
- Apply `19-lifecycle-orchestration` whenever a contact can qualify for multiple flows or channels so one contact-level policy owns precedence, caps, deduplication, suppression, and holdouts. [BRAZE-STRAT-01][HUB-WF-01]
- Identify never-engaged or persistently inactive contacts, make at most a deliberate final re-engagement attempt, then suppress non-responders. [KL-NEVER-01][KL-SUNSET-01]

## 5. Creative and accessibility gate
- Use a recognizable sender, descriptive subject, concise hierarchy, and one clearly dominant action. [MC-SUBJ-01][BRAZE-CTA-01][BRAZE-STRAT-01]
- Use responsive layouts, live text for essential information, meaningful ALT text, sufficient contrast, readable hierarchy, and large tappable controls. [LIT-ACCESS-01][LIT-MOBILE-01]
- Ensure the message still makes sense with images disabled and provide a usable plain-text version. [LIT-QA-01][AWS-SES-FORMAT-01]
- Provide safe fallbacks for missing personalization and never expose raw merge tags. [LIT-QA-01]

## 6. Measurement and experimentation gate
- Give every campaign one primary business objective and KPI mapped to its lifecycle stage. [BRAZE-STRAT-01][BRAZE-METRIC-01]
- Add consistent campaign/link tracking and measure the downstream conversion event, revenue, retention, qualified reply, or pipeline result. [MC-GA-01][MC-CONV-01][HUB-B2B-01]
- Use opens only as a secondary directional signal because privacy protection can create inaccurate opens and timing. [LIT-MPP-01]
- Test one major variable at a time unless a properly designed multivariate test has enough traffic, and name the winning metric before launch. [MC-AB-01][HUB-AB-01]
- Use a sampled control/holdout when volume and tooling permit so the team can estimate incremental lift instead of relying only on attributed conversions. [KL-SEGTEST-01]

## 7. Pre-send QA gate
- Verify audience counts, exclusions, consent, suppression, frequency conflicts, trigger logic, exit conditions, and fallback paths. [HUB-WF-01][GMAIL-01]
- Verify sender, subject, preview, legal footer, unsubscribe, reply path, dates, prices, terms, product availability, and every factual claim. [FTC-01][MC-SPAM-01]
- Validate every link and UTM, dynamic field, coupon/code, landing page, conversion event, and analytics integration. [LIT-QA-01][MC-GA-01]
- Test rendering across major mobile, desktop, and webmail clients, with images off and in dark mode; check ALT text, contrast, and plain text. [LIT-QA-01][LIT-TEST-01]
- Send seed/test messages and confirm authentication and delivery before enabling the full audience. [LIT-TEST-01][GMAIL-03]

## Do / Don't digest
**Do**
- Authenticate every sending domain with SPF and DKIM, and aligned DMARC for bulk sending. [GMAIL-01][YAHOO-01]
- Send only where permission or another documented lawful basis exists for this channel and purpose. [ICO-02][HUB-CONSENT-01][MC-PERM-01]
- Keep the list clean: suppress bounces, complaints, and unsubscribes immediately, and sunset persistently unengaged contacts. [KL-SUNSET-01][KL-NEVER-01][GMAIL-01]
- Make unsubscribing easy: a visible link plus one-click unsubscribe, honored within 48 hours. [GMAIL-01][YAHOO-01][MC-SPAM-01]
- Personalize from reliable first-party data with safe fallbacks. [MC-SEG-01][LIT-QA-01]
- Optimize for mobile: responsive layout, live text, and large tappable controls. [LIT-MOBILE-01][LIT-ACCESS-01]
- Test before sending: major clients, images off, dark mode, plain text, and seed sends. [LIT-QA-01][LIT-TEST-01]

**Don't**
- Don't buy, rent, scrape, or harvest lists. [MC-LISTS-01][ICO-04]
- Don't over-mail: respect frequency caps and preferences, and keep the Gmail spam rate below 0.1%, never at or above 0.3%. [GMAIL-02][BRAZE-HOLIDAY-01][BRAZE-STRAT-01]
- Don't use clickbait: the subject and preview must truthfully represent the content. [FTC-01][MC-SUBJ-01]
- Don't send without one clear primary call to action. [BRAZE-CTA-01][BRAZE-STRAT-01]
- Don't judge success or trigger automation on opens alone. [LIT-MPP-01]
- Don't disguise marketing as transactional or service mail. [BRAZE-TRANS-01][FTC-01]

## Decision rule
- Return `BLOCK` when permission, legality, authentication, suppression, identity, or factual claims cannot be verified. [FTC-01][ICO-02][GMAIL-01]
- Return `HOLD` when the campaign is lawful but data, tracking, QA, inventory, landing page, or approvals are incomplete. [LIT-QA-01][LIT-TEST-01]
- Return `SEND` only when every applicable gate passes and the campaign has a measurable hypothesis. [BRAZE-STRAT-01][BRAZE-METRIC-01]
