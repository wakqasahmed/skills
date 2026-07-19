# SEO/AEO/GEO audit outcome eval

`python3 check-contract.py` is the credential-free PR-CI layer. It validates
the skill's non-negotiable audit boundaries and the held-out manifest shape; it
does not score an agent.

The manually gated `seo-aeo-geo-audit-harness` workflow runs five trials of
every held-out case in both conditions. `run_harness.py` creates a fresh
temporary workspace per trial. The checked-in `run_target_agent.py` is only an
adapter: it sends the prompt, observations, declared model, and — only when
enabled — the actual `SKILL.md` and `checks.md` to
`/usr/local/bin/seo-aeo-geo-audit-agent` in the pinned evaluator image. The
image is the approved external target-agent evaluator; it must return the
requested model plus its concrete model version. The adapter contains no audit
logic or expected outcomes.
The container is read-only, networkless, credentialless, and has no mounted
repository or home directory.

The runner emits one JSON object with protocol version
`seo-aeo-geo-artifact-runner/v1`, `model`, `model_version`, `skill_used`, and
an `audit_artifact` object.
`skill_used` must be true only for enabled audit requests; it is false for
disabled trials and enabled do-not-use requests. The artifact
must contain a disposition, structured finding IDs, recommendation IDs, and
evidence source records. `validate-harness-results.py` checks those artifacts
against independently held outcome fixtures; it does not search prose or
accept runner-supplied pass labels. Every enabled case needs an 80% pass rate
and enabled results must improve by at least two percentage points over
disabled. The workflow retains the result JSON artifact for comparisons.
