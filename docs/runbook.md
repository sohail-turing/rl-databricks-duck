# Runbook

> How to operate the harness day-to-day.
> Status: **stub — to be filled during WS-8/WS-10**.

## Prerequisites
- Python 3.11+
- `pip install -r requirements.txt`
- `.env` configured (copy from `.env.example`)

## Generate the workspace (after access lands)
```bash
python -m workspace.generators.run --target databricks
```

## Run a single task
```bash
python -m harness.runner --task T-001 --run-id local-001
```

## Run the full suite
```bash
python -m harness.runner --suite tasks/ --concurrency 4
```

## Verify a distractor / anchor claim
```bash
python -m harness.runner \
  --task T-042 \
  --claim D-3 \
  --ablation on \
  --runs 30
```
Output goes to `verification/runs/T-042/D-3/`.

## Generate the coverage matrix
```bash
python tools/coverage_matrix.py
```
Reads `tasks/*.yaml` + `verification/reports/*.yaml`, writes `verification/coverage.md`.
