# Remediation plan verification checks

This skill converts other audits' findings into tickets — it does not run its own discovery
crawl. Its checks are about making each ticket's acceptance criteria machine-verifiable, using
the same commands the source audit skill already used to find the issue.

## Attach a re-runnable verification command to every ticket

For each finding, carry forward (or write, if missing) the exact command that will flip from
failing to passing once the fix ships. Reuse the relevant skill's `references/checks.md`:

- Crawler/robots fixes → `robots-ai-crawler-audit/references/checks.md`
- Sitemap/discovery fixes → `sitemap-discovery-audit/references/checks.md`
- Structured data fixes → `schema-markup-audit/references/checks.md`
- `llms.txt` fixes → `llms-txt-generator/references/checks.md`
- Content gap fixes → `answer-engine-content-audit/references/checks.md`
- Citation/trust fixes → `citation-readiness-audit/references/checks.md`

Example ticket acceptance criterion, copied verbatim from the source check:

```bash
curl -s -o /dev/null -w "%{http_code}\n" -A "GPTBot" "$URL"
# expect: 200 (was: 403)
```

## Sanity-check ticket independence before finalizing

```bash
grep -c '^## ' remediation-plan.md   # one heading per ticket, not one giant block
```

Confirm no single ticket mixes a crawler-access fix, a schema fix, and a content rewrite —
each should be independently verifiable with its own command and its own before/after state.

## Confirm blockers needing human/owner action are marked, not silently dropped

```bash
grep -inE 'credential|access|legal|policy owner|cms access|approval' remediation-plan.md
```

Any ticket matching this pattern must carry an explicit "blocked on" note rather than a
verification command, since it can't be closed by running a check.

## Evidence discipline

Every ticket must have either a re-runnable command with an expected before/after result, or an
explicit human-blocker note. A ticket with neither is not execution-ready — send it back to the
source audit skill for more specific findings.
