# Wakqasahmed Skills [![skills.sh](https://skills.sh/b/wakqasahmed/skills)](https://skills.sh/wakqasahmed/skills)

The canonical home for Wakqasahmed's public AI visibility, agentic commerce, engineering workflow, PHP, Laravel, Filament, and email marketing skills.

## Install

```bash
npx skills@latest add wakqasahmed/skills
```

The installer discovers the complete catalogue. Automated agent installs select all listed skills.

## Quickstart

1. Install with the command above.
2. Run `workflow-router setup` once in the target repository. It detects the tracker, branch, labels, instructions, docs, and test/runtime conventions, then shows any proposed changes for approval.
3. Ask `workflow-router` for the current situation.

Example: `workflow-router Checkout now returns 500 after coupon changes.` routes to diagnose → regression test → smallest fix → review gate, because the failure must be reproduced before changing code and retained as a regression check.

## Browse Skills

skills.sh does not support repository-defined marketplace groups. Use this category-first catalogue to choose a relevant skill, then keep the canonical installer above for the complete set.

### Agentic Commerce

- [Agent Readiness](skills/agentic-commerce/agent-readiness/)
- [Commerce Protocol Readiness](skills/agentic-commerce/commerce-protocol-readiness/)
- [Custom Agent Remediation Plan](skills/agentic-commerce/custom-agent-remediation-plan/)
- [Ecommerce Policy Readiness](skills/agentic-commerce/ecommerce-policy-readiness/)
- [FDE Opportunity Map](skills/agentic-commerce/fde-opportunity-map/)
- [LLMs.txt and Crawler Access](skills/agentic-commerce/llms-txt-and-crawler-access/)
- [Product Knowledge Gap Analysis](skills/agentic-commerce/product-knowledge-gap-analysis/)
- [Readiness Audit](skills/agentic-commerce/readiness-audit/)
- [SEO, AEO, and GEO Audit](skills/agentic-commerce/seo-aeo-geo-audit/)
- [Skills Marketplace Readiness](skills/agentic-commerce/skills-marketplace-readiness/)

### AI Visibility

- [AI Search Remediation Plan](skills/ai-visibility/ai-search-remediation-plan/)
- [AI Visibility Audit](skills/ai-visibility/ai-visibility-audit/)
- [Answer Engine Content Audit](skills/ai-visibility/answer-engine-content-audit/)
- [Citation Readiness Audit](skills/ai-visibility/citation-readiness-audit/)
- [LLMs.txt Generator](skills/ai-visibility/llms-txt-generator/)
- [Robots AI Crawler Audit](skills/ai-visibility/robots-ai-crawler-audit/)
- [Schema Markup Audit](skills/ai-visibility/schema-markup-audit/)
- [Sitemap Discovery Audit](skills/ai-visibility/sitemap-discovery-audit/)

### Email Marketing

- [Email Marketing Guardrails](skills/email-marketing/00-email-marketing-guardrails/)
- [Newsletter Editorial](skills/email-marketing/01-newsletter-editorial/)
- [Welcome Onboarding](skills/email-marketing/02-welcome-onboarding/)
- [Lead Nurture Education](skills/email-marketing/03-lead-nurture-education/)
- [Promotional Offer](skills/email-marketing/04-promotional-offer/)
- [Product Launch](skills/email-marketing/05-product-launch/)
- [Event Webinar](skills/email-marketing/06-event-webinar/)
- [Abandoned Cart](skills/email-marketing/07-abandoned-cart/)
- [Browse Abandonment](skills/email-marketing/08-browse-abandonment/)
- [Post Purchase Customer Success](skills/email-marketing/09-post-purchase-customer-success/)
- [Review Feedback Survey](skills/email-marketing/10-review-feedback-survey/)
- [Cross Sell Upsell](skills/email-marketing/11-cross-sell-upsell/)
- [Replenishment Renewal](skills/email-marketing/12-replenishment-renewal/)
- [Winback Reengagement Sunset](skills/email-marketing/13-winback-reengagement-sunset/)
- [Transactional Service](skills/email-marketing/14-transactional-service/)
- [B2B Outbound Prospecting](skills/email-marketing/15-b2b-outbound-prospecting/)
- [Inventory Price Alert](skills/email-marketing/16-inventory-price-alert/)
- [Loyalty VIP Referral](skills/email-marketing/17-loyalty-vip-referral/)
- [Jurisdiction Compliance Routing](skills/email-marketing/18-jurisdiction-compliance-routing/)
- [Lifecycle Orchestration](skills/email-marketing/19-lifecycle-orchestration/)
- [List Growth Signup Preferences](skills/email-marketing/20-list-growth-signup-preferences/)
- [Deliverability Sender Operations](skills/email-marketing/21-deliverability-sender-operations/)

### Engineering Workflow

- [AI Agent PR Metadata](skills/engineering/ai-agent-pr-metadata/)
- [Changesets Release](skills/engineering/changesets-release/)
- [Clarify Work](skills/engineering/clarify-work/)
- [Decompose to Issues](skills/engineering/decompose-to-issues/)
- [Define Done](skills/engineering/define-done/)
- [HITL Blocker](skills/engineering/hitl-blocker/)
- [Release Gate](skills/engineering/release-gate/)
- [Review Gate](skills/engineering/review-gate/)
- [Subagent Pipeline](skills/engineering/subagent-pipeline/)
- [To PRD](skills/engineering/to-prd/)
- [Workflow Router](skills/engineering/workflow-router/)

### PHP/Laravel/Filament

- [PHP Principles](skills/php/php-principles/)

- [Laravel Conventions](skills/laravel/laravel-conventions/)
- [Laravel Security](skills/laravel/laravel-security/)
- [Laravel Testing](skills/laravel/laravel-testing/)

- [Filament Conventions](skills/filament/filament-conventions/)
- [Filament Plugin First](skills/filament/filament-plugin-first/)
- [Livewire Conventions](skills/filament/livewire-conventions/)

### Productivity/Product

- [Roast](skills/product/roast/)

- [Handover](skills/productivity/handover/)

## Repo Layout

```text
skills/
  ai-visibility/
  agentic-commerce/
  engineering/
  product/
  productivity/
  filament/
  laravel/
  php/
  email-marketing/
support/
  ai-engineering-workflow/
  email-marketing/
```

## Validate

```bash
python3 scripts/validate-plugin.py
python3 support/email-marketing/scripts/validate-citations.py
python3 support/email-marketing/scripts/validate-orchestration.py
python3 support/email-marketing/scripts/validate-list-growth.py
python3 support/email-marketing/scripts/validate-deliverability.py
bash support/ai-engineering-workflow/scripts/test-ai-agent-pr-metadata.sh
python3 -m unittest tests/test_pr_governance.py
bash support/ai-engineering-workflow/scripts/test-install-user.sh
```

## Security

Skills are Markdown instruction files, not executable code. See [SECURITY.md](SECURITY.md) for what that means, which skills instruct running shell commands or fetching URLs, and how to report a concern.
