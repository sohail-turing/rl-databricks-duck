# Runbook

> How to operate the harness day-to-day.
> Status: **stub — to be filled during WS-8/WS-10**.

## Prerequisites
- Python 3.11+
- `pip install -r requirements.txt`
- `.env` configured (copy from `.env.example`)

## Generate the local milestone slice

```bash
.venv/bin/python -m workspace.generators.run \
  --target sqlite \
  --build tier-c \
  --out verification/runs/tier_c_seed.sqlite \
  --csv-dir verification/exports/tier_c_csv \
  --schema-json-dir verification/schema/tier_c_json
```

## Query the local SQLite artifact with canonical names

```bash
.venv/bin/python tools/sqlite_query.py --list-mapping
.venv/bin/python tools/sqlite_query.py --sql "select branch_id, sum(fee_amount_usd) as total_fee from main.finance_core.fee_revenue group by 1 order by 2 desc limit 5"
```

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
