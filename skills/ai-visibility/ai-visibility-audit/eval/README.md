# ai-visibility-audit eval fixture

A frozen, offline fixture that checks the `ai-visibility-audit` skill's contract
without a live network call or an LLM in the loop.

`run_eval.py` does not invoke `SKILL.md` or an LLM — skills are prompt files with no
code path to execute directly. Instead it is a hand-maintained Python
reimplementation of the commands in `../references/checks.md`, run against the fixture
and asserted against the severity/evidence/delegation/guardrail rules `SKILL.md`
documents. It proves the fixture and the assertions are internally consistent and
regression-safe; it does not prove an LLM following `SKILL.md` will produce this exact
output. If `checks.md` or `SKILL.md`'s workflow changes, update the matching
`check_*` function here too — nothing else will catch the drift.

## What it checks

`fixture/` is a saved snapshot with three injected issues of differing severity:

| Issue | Fixture file | Severity |
|---|---|---|
| `robots.txt` blocks `GPTBot` from the whole site | `fixture/robots.txt` | critical |
| No JSON-LD structured data on the page | `fixture/index.html` | important |
| FAQ answers are too thin to cite | `fixture/index.html` | optional |

`run_eval.py` re-implements the checks documented in `../references/checks.md`
against the local fixture files instead of shelling out to `curl` against a
live site, builds a ranked findings report in the shape the skill is expected
to produce, then asserts:

1. all 3 injected issues are surfaced,
2. each is ranked with the correct severity tier (critical / important / optional),
3. each has an evidence citation (file + line or matched content, not just a claim),
4. at least one finding names the correct delegate skill for a deep dive
   (`robots-ai-crawler-audit`, `schema-markup-audit`, or `answer-engine-content-audit`),
5. the report contains no inclusion/ranking guarantee language, per the skill's
   guardrails.

## Run it

```bash
python3 skills/ai-visibility/ai-visibility-audit/eval/run_eval.py
```

Exits `0` and prints `PASS: ...` when all assertions hold, exits `1` and prints
`FAIL:` with the specific failing assertions otherwise.

## Extending it

To add a new fixture case:

1. Edit or add a file under `fixture/` with the new injected issue.
2. Add a `check_*` function in `run_eval.py` that mirrors a specific command
   from `../references/checks.md` (or a specific step of `SKILL.md`'s
   workflow) and returns a finding dict (`severity`, `title`, `evidence`,
   `delegate`) or `None`.
3. Add the new check to the `run_audit()` pipeline.
4. If the new issue should be required for a pass, extend `assert_report()`.

Keep fixtures small, static, and free of live network calls — this eval must
stay deterministic and runnable offline.
