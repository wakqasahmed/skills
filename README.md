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

```bash
npx skills@latest add wakqasahmed/skills
```

## Install Individual Packs

```bash
npx skills@latest add wakqasahmed/ai-visibility-skills
npx skills@latest add wakqasahmed/agentic-commerce-skills
npx skills@latest add wakqasahmed/ai-engineering-workflow-skills
```

## Included Packs

- `ai-visibility-skills`: AI search visibility, `llms.txt`, crawler access, schema, sitemap, answer-engine content, and citation readiness.
- `agentic-commerce-skills`: ecommerce audits, crawler access, protocol readiness, policy readiness, and remediation planning.
- `ai-engineering-workflow-skills`: clarify work, define done, decompose scope, review gates, release gates, handoffs, and HITL blockers.

## Repo Layout

```text
skills/
  ai-visibility/
  agentic-commerce/
  engineering-workflow/
```

The source repos remain canonical. This repo is the all-skills distribution surface.

## Sync From Source

```bash
scripts/sync-from-source.sh
```

That refreshes the copied skill folders from:

- `/opt/OSS-contributions/ai-visibility-skills`
- `/opt/OSS-contributions/agentic-commerce-skills`
- `/opt/OSS-contributions/ai-engineering-workflow-skills`

## Validate

```bash
python3 scripts/validate-plugin.py
```
