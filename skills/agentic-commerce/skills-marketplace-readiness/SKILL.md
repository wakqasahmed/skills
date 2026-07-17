---
name: skills-marketplace-readiness
description: Prepare an agent skills repository for discovery, installation, and marketplace listings. Use when publishing skills to skills.sh, Agent Skills clients, Claude plugins, Codex, Cursor, Copilot, and related skill directories.
---

# Skills Marketplace Readiness

## Workflow

1. Confirm every skill is an independent folder with a matching `SKILL.md` frontmatter `name` and a specific activation-focused `description`.
2. Keep each skill narrow, executable, and short enough for progressive disclosure. Move long background material to references only when needed.
3. Add install and discovery surfaces:
   - README install command: `npx skills@latest add owner/repo`
   - skills.sh badge: `[![skills.sh](https://skills.sh/b/owner/repo)](https://skills.sh/owner/repo)`
   - `.claude-plugin/plugin.json` with all published skill paths.
   - `scripts/list-skills.sh` and `scripts/link-skills.sh` for local fallback.
4. Validate that all plugin paths resolve and each listed skill has a `SKILL.md`.
5. Confirm safety-relevant skills — those that can drive autonomous checkout, payment, support actions, or other agent-executed changes — have a behavioral eval (fixtures plus a pass/fail runner) wired into CI. A skill that only has prose guardrails and no eval coverage is not marketplace-ready.
6. Position the repo around searchable intent, not internal naming: use words buyers and agents search for, such as ecommerce, agentic commerce, AEO, GEO, SEO, agent readiness, checkout, ACP, UCP, MCP, and AI crawler readiness.
7. Submit or seed marketplace visibility by installing with the public CLI, sharing the GitHub URL, adding the badge, and linking the repo from website, docs, social profiles, and relevant skill directories.

## Guardrails

- Do not inflate install claims or marketplace status before the repo appears publicly.
- Do not bundle unrelated workflow skills into the domain repo. Keep engineering workflow skills in a separate repo.
- Treat marketplace listings as distribution, not validation. Skill quality still depends on real execution and iteration.
- Do not call a pack marketplace-ready if a safety-relevant skill lacks behavioral eval or CI coverage.
