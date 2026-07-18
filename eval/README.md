# Trigger evaluations

`run-trigger-evals.py` is a deterministic, offline proxy for description routing. For each case it reads the target `SKILL.md` frontmatter description and activates only when the prompt shares at least two meaningful words with that live description. It uses no network service, model, or credential.

Each case is a complete positive/negative pair assigned to `train` or `validation`; a pair is never split. The CI job runs `--split validation`, so held-out prompts are not loaded for training metrics. `--split train` is available for intentional tuning, while `--split all` is a coverage check.

Run:

```sh
python3 eval/run-trigger-evals.py --split validation
```
