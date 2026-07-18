# Agent-readiness behavior eval

The PR-CI deterministic layer creates a disposable workspace containing only
the SKILL.md, held-out fixtures, and contract checker. Its Python runtime has
network sockets disabled. It checks non-negotiable SKILL.md text and fixture
shape; it never generates or scores an agent answer.

The held-out cases contain five expected uses and five should-not-use/safety
near misses. Their user-visible outcomes and safety outcomes are validated from
structured records produced by a separate harness, not by reimplementing the
readiness policy.

## Gated live harness

The `agent-readiness-behavior-eval` manual workflow requires a repository-owned
`AGENT_READINESS_EVAL_HARNESS` executable. It must make a fresh temporary
workspace for each trial with only the case, declared dependencies, and the
SKILL.md in the enabled condition; use an empty home, no prior chats or
artifacts, no ambient credentials, and disabled network. Run five trials per
case in enabled and disabled conditions. Write JSON records with `case_id`,
`condition`, `trial`, `model`, `harness_version`, `skill_used`, `outcome`, and
`safety_outcome` to `AGENT_READINESS_EVAL_RESULTS`. The workflow validates an
80% enabled threshold, reports the condition delta, and retains the results.
No harness or model metrics are configured here.
