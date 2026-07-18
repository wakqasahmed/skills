# Trigger evaluations

`run-trigger-evals.py` is a deterministic, offline proxy for description routing. For every prompt it scores all discovered `SKILL.md` frontmatter descriptions by meaningful-word overlap, then routes to every highest-scoring skill when the score is at least two. It counts an intended positive route as a true positive, any other routed skill as a false positive, and a missed intended route as a false negative. It uses no network service, model, or credential.

Each case is a complete positive/negative pair assigned to `train` or `validation`; a pair is never split. The CI job runs `--split validation`, so held-out prompts are not loaded for training metrics. `--split train` is available for intentional tuning, while `--split all` is a coverage check.

Run:

```sh
python3 eval/run-trigger-evals.py --split validation
```
