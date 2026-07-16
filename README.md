# Wakqasahmed Skills [![skills.sh](https://skills.sh/b/wakqasahmed/skills)](https://skills.sh/wakqasahmed/skills)

Single-command install surface for Wakqasahmed's AI visibility, agentic commerce, and AI engineering workflow skill packs.

## Most Useful Starting Point

```bash
npx skills@latest add wakqasahmed/ai-visibility-skills
```

Ask your agent:

```text
Audit my site for ChatGPT, Claude, Perplexity, Google AI Overviews, llms.txt, schema, crawler access, sitemap coverage, and citation readiness.
```

## Install Everything

Use the aggregate pack when you want all included skills from one install path:

```bash
npx skills@latest add wakqasahmed/skills
```

## Install Individual Packs

Use these only when you want one source pack instead of the aggregate bundle:

```bash
npx skills@latest add wakqasahmed/ai-visibility-skills
npx skills@latest add wakqasahmed/agentic-commerce-skills
npx skills@latest add wakqasahmed/ai-engineering-workflow-skills
npx skills@latest add wakqasahmed/php-laravel-filament-skills
npx skills@latest add wakqasahmed/email-marketing-skills
```

## Included Packs

- `ai-visibility-skills`: AI search visibility, `llms.txt`, crawler access, schema, sitemap, answer-engine content, and citation readiness.
- `agentic-commerce-skills`: ecommerce audits, crawler access, protocol readiness, policy readiness, and remediation planning.
- `ai-engineering-workflow-skills`: clarify work, define done, decompose scope, subagent pipeline, review gates, release gates, idea roasting, handovers, and HITL blockers. The aggregate mirrors the current source manifest.
- `php-laravel-filament-skills`: PHP, Laravel, and Filament conventions and plugin-first design principles.
- `email-marketing-skills`: newsletter, lifecycle, lifecycle orchestration, transactional, and deliverability skills covering the full email marketing calendar from welcome through winback.

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
```

The source repos remain canonical. This repo is the all-skills distribution surface.

## Sync From Source

```bash
scripts/sync-from-source.sh ../ai-visibility-skills ../agentic-commerce-skills ../ai-engineering-workflow-skills ../php-laravel-filament-skills ../email-marketing-skills
```

That refreshes the copied skill folders from local clones of the five source packs. You can also pass those paths with `VISIBILITY_SOURCE`, `COMMERCE_SOURCE`, `WORKFLOW_SOURCE`, `LARAVEL_SOURCE`, and `EMAIL_MARKETING_SOURCE`.

## Validate

```bash
python3 scripts/validate-plugin.py
```

## Security

Skills are Markdown instruction files, not executable code. See [SECURITY.md](SECURITY.md) for what that means, which skills instruct running shell commands or fetching URLs, and how to report a concern.
