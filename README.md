# Wakqasahmed Skills [![skills.sh](https://skills.sh/b/wakqasahmed/skills)](https://skills.sh/wakqasahmed/skills)

The canonical home for Wakqasahmed's public AI visibility, agentic commerce, engineering workflow, PHP, Laravel, Filament, and email marketing skills.

## Install

```bash
npx skills@latest add wakqasahmed/skills
```

The installer discovers the complete catalogue. Automated agent installs select all listed skills.

## Browse Skills

- `ai-visibility`: AI search visibility, `llms.txt`, crawler access, schema, sitemap, answer-engine content, and citation readiness.
- `agentic-commerce`: ecommerce audits, protocol readiness, policy readiness, and remediation planning.
- `engineering`, `product`, and `productivity`: planning, delivery, review gates, releases, handovers, and HITL blockers.
- `php`, `laravel`, and `filament`: language, framework, and plugin-first design conventions.
- `email-marketing`: newsletter, lifecycle, transactional, and deliverability skills from welcome through winback.

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
