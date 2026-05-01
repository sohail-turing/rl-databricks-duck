# Data Generators

This folder is the active generator layer for the current 10-task Meridian Trust milestone.

## Current build tiers

1. `milestone.py` -> Tier A shared dimensions and first gold tables
2. `tier_b.py` -> Tier B medium-task tables
3. `tier_c.py` -> Tier C hard-task tables
4. `run.py` -> CLI entrypoint

## Current output modes

| Output | Why it exists |
| --- | --- |
| SQLite | canonical local validation database |
| CSV | easy table-by-table review for the team |
| JSON schema | portable table-structure handoff |

## Common commands

```bash
.venv/bin/python -m workspace.generators.run --target sqlite --out ./verification/runs/tier_a_seed.sqlite
.venv/bin/python -m workspace.generators.run --target sqlite --build tier-b --out ./verification/runs/tier_b_seed.sqlite
.venv/bin/python -m workspace.generators.run --target sqlite --build tier-c --out ./verification/runs/tier_c_seed.sqlite --csv-dir ./verification/exports/tier_c_csv --schema-json-dir ./verification/schema/tier_c_json
```

To generate more rows, keep the same command and raise `--scale`.

## Preferred local query path

Use canonical table names locally through the helper:

```bash
.venv/bin/python tools/sqlite_query.py --list-mapping
.venv/bin/python tools/sqlite_query.py --sql "select branch_id, sum(fee_amount_usd) as total_fee from main.finance_core.fee_revenue group by 1 order by 2 desc limit 5"
```

This avoids memorizing physical SQLite table names like `finance_core__fee_revenue`.

## Current limitation

The Databricks target is still intentionally unimplemented. The current working generator flow is local and SQLite-first.
