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

## Optional OpenRouter live eval

The default runner remains `isolated`; it is the only runner that uses the
pinned image and Docker network isolation. OpenRouter is an explicit,
manually selected live-eval runner, never pull-request CI. It executes the
checked-in adapter directly on the GitHub-hosted runner. The adapter uses the
fixed `https://openrouter.ai/api/v1/chat/completions` endpoint. It sends each
held-out prompt, observations, and enabled skill/check content to OpenRouter.
Do not use real customer, production, or secret data in the fixtures; provider
logging and retention may apply.

Set these repository settings before dispatching it:

- Actions secret `OPENROUTER_API_KEY`: an OpenRouter key. It is injected only
  into the OpenRouter workflow step and is never written to artifacts or code.
- Actions variable `SEO_AEO_GEO_AUDIT_EVAL_MODEL`:
  `nvidia/nemotron-3-super-120b-a12b:free`.
- Actions variable `SEO_AEO_GEO_AUDIT_EVAL_MODEL_VERSION`: the concrete
  version/date approved for this run. The result artifact records it verbatim.

In Actions, dispatch `SEO AEO GEO audit harness`, set `run_harness` to true,
select `openrouter`, and use the protected `main` branch. The secret-backed
step is skipped for every other ref. It runs five enabled and five disabled trials per
held-out case, validates the artifact outcomes, and uploads the JSON results.
The runner retries HTTP 429 responses up to five times and honors provider
`Retry-After` or `X-RateLimit-Reset` delays when supplied; free-model capacity
can still make a run take longer or fail after those bounded retries.
For a local run, export `OPENROUTER_API_KEY` only in the invoking shell and run:

```bash
python3 skills/agentic-commerce/seo-aeo-geo-audit/eval/run_harness.py \
  --runner openrouter \
  --model nvidia/nemotron-3-super-120b-a12b:free \
  --model-version approved-version-or-date \
  --trials 5 \
  --output seo-aeo-geo-audit-results.json
python3 skills/agentic-commerce/seo-aeo-geo-audit/eval/validate-harness-results.py \
  --results seo-aeo-geo-audit-results.json
```

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
