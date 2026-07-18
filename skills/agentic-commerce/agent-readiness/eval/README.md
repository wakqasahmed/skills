# Agent-readiness behavior eval

`bash skills/agentic-commerce/agent-readiness/eval/run-eval.sh` evaluates ten held-out, synthetic storefront snapshots with no network, credentials, or prior workspace artifacts. The user-visible outcome is a readiness report that separates read readiness from action readiness and names evidence-backed blockers.

The deterministic layer checks the non-negotiable outcome boundary, not skill loading. A credentialed clean-workspace harness remains a follow-up: it must run the declared model/harness 3–6 times per fixture with and without `SKILL.md`, retain both reports, and require at least an 80% pass rate plus a positive skill-enabled outcome delta before adoption.
