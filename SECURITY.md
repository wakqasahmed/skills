# Security Policy

## What this repository is

This repository distributes [Agent Skills](https://skills.sh) — Markdown instruction files (`SKILL.md`, plus reference docs) that an AI agent reads and follows. **They are not executable code.** Installing a skill does not run a binary, does not execute a build step, and does not add a dependency to your project. The skill content only takes effect when an AI agent reads it and chooses to act on it.

That said, several skills instruct the agent to *run shell commands* on your behalf (for example, `curl` requests against a site under audit) or to fetch remote URLs as part of their workflow. Because an agent that has installed a skill typically has broader tool access (shell, file system, network) than the skill file itself, any commands or fetches a skill recommends are executed with **whatever permissions your agent session already has** — not permissions granted by the skill. Review a skill's `SKILL.md` and any `references/` files before installing it, the same way you would review a script before running it.

### Skills in this repo that instruct running shell commands or fetching URLs

This list covers the skills whose workflow explicitly runs `curl`/shell commands or names fetching a URL as a step. It is representative, not a guaranteed-exhaustive audit — many other skills describe "checking" or "reviewing" a site's pages, which an agent may also carry out via a URL fetch depending on the tools it has available.

- `skills/agentic-commerce/agent-readiness/references/checks.md` — runs `curl` against the site under audit (robots.txt, headers, bot user-agents).
- `skills/ai-visibility/ai-visibility-audit/references/checks.md` — runs `curl` against the site under audit (robots.txt, redirects, meta tags, structured data).
- `skills/ai-visibility/schema-markup-audit/references/checks.md` — runs `curl` to fetch page HTML for schema/structured-data checks.
- `skills/ai-visibility/robots-ai-crawler-audit/SKILL.md` — step 1 fetches `/robots.txt`, then checks headers and tags on key URLs.
- `skills/ai-visibility/sitemap-discovery-audit/SKILL.md` — finds sitemap declarations and checks representative URLs for status codes, redirects, and canonical tags.
- `skills/agentic-commerce/llms-txt-and-crawler-access/SKILL.md` — checks `robots.txt`, sitemap availability, and `llms.txt` existence.

All of the above fetch only the target site the user is auditing (via a `$SITE`/`$URL`/`$PDP` variable, or the site named in the conversation) — they do not fetch arbitrary third-party endpoints or exfiltrate data.

## Reporting a security concern

If you find a skill in this repository that:

- instructs an agent to run a command or fetch a URL in a way that could exfiltrate data, install unexpected software, or otherwise act against the interests of the person running it, or
- contains a prompt-injection risk (e.g. content designed to make an agent ignore its instructions or a user's intent),

please report it by opening a [GitHub issue](https://github.com/wakqasahmed/skills/issues/new) in this repository. Include:

- the skill path (e.g. `skills/<category>/<skill-name>/SKILL.md`)
- the specific instruction or line you're concerned about
- why you believe it's unsafe

There is no separate private disclosure channel at this time — file a public issue. If the concern involves sensitive details you'd rather not post publicly, note that in the issue title and we'll follow up to arrange a private channel.

## Scope

This policy covers the content of the skill files in this repository (`skills/`) and the sync/validation scripts in `scripts/`. It does not cover the `skills@latest` install CLI, GitHub itself, or the security of any site you choose to audit with these skills.
