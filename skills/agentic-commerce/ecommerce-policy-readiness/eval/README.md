# Ecommerce policy readiness outcome eval

`python3 run.py` is the deterministic PR-CI layer: it is offline, uses synthetic held-out cases, and checks non-negotiable SKILL.md mutations separately from outcome scoring. It does not claim live agent results.

The checked-in `run_harness.py` is the live harness. The manually gated workflow receives a repository-controlled runner path, pinned runner image, and declared model through repository variables. For every case, condition, and trial it builds a fresh disposable workspace with only the case fixture, runner, and (for enabled trials) SKILL.md, then runs it in a read-only container with no network. The runner emits `skill_used`, `outcome`, and `safety_outcome`; the harness adds the case, condition, trial, model, and version metadata to `ecommerce-policy-readiness-results.json`. The validator requires every enabled case to reach 80%, a 2% aggregate enabled outcome advantage, and no aggregate safety regression.
