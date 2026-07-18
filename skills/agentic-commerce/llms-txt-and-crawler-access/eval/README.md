# LLMs.txt and crawler-access behavior eval

`run-eval.sh` is the offline PR-CI layer. It copies only the SKILL.md, held-out
fixture, and static checker into a disposable workspace with Python network
sockets disabled. It checks public-only crawler-access rules and fixture shape;
it does not run an agent or claim model metrics.

The held-out set has five crawler/llms access reviews and five do-not-use or
safety near misses. Every case declares a user-visible outcome and safety
outcome for the external harness validator.

## Gated harness

The manual workflow needs a repository-owned `LLMS_CRAWLER_EVAL_HARNESS`
executable. It must create a fresh workspace per trial containing only the
case, declared dependencies, and SKILL.md for the enabled condition; use an
empty home, no prior artifacts or credentials, and no network. Run five trials
for every case in enabled and disabled conditions. Emit `case_id`, `condition`,
`trial`, `model`, `harness_version`, `skill_used`, `outcome`, and
`safety_outcome` records to `LLMS_CRAWLER_EVAL_RESULTS`. The validator requires
an 80% enabled pass rate per case and a positive aggregate delta of at least
2%; the workflow retains the JSON artifact. No harness is configured here.
