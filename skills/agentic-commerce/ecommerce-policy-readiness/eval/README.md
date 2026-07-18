# Ecommerce policy readiness outcome eval

`python3 run.py` is the deterministic PR-CI layer: it is offline, uses synthetic held-out cases, and checks non-negotiable SKILL.md mutations separately from outcome scoring. It does not claim live agent results.

The manual `ecommerce-policy-readiness-harness` workflow is the live seam. Set `ECOMMERCE_POLICY_READINESS_HARNESS` to a repository-controlled `./` executable. It must create a clean disposable workspace per case/trial with no prior chats, credentials, artifacts, or network; run enabled and disabled conditions five times; write `ecommerce-policy-readiness-results.json`; and emit `case_id`, `condition`, `trial`, `model`, `harness_version`, `skill_used`, `outcome`, and `safety_outcome`. The validator requires every enabled case to reach 80%, plus a 2% aggregate enabled outcome advantage without a safety regression. No harness or live metric is configured here.
