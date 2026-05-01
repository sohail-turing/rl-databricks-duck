# Tools

Utility scripts used across the current milestone.

## Current scripts

| Script | Status | Purpose |
| --- | --- | --- |
| `sqlite_query.py` | active now | Runs SQL against the local SQLite artifact while keeping canonical table names |
| `validate_task_specs.py` | active when task files exist | Validates `tasks/*.yaml` against the documented task schema |
| `coverage_matrix.py` | later program stage | Builds taxonomy coverage once verified claims exist |
| `stats.py` | later program stage | Fisher's exact and odds-ratio helper for full claim verification |

## Preferred day-to-day helper

```bash
.venv/bin/python tools/sqlite_query.py --list-mapping
.venv/bin/python tools/sqlite_query.py --sql "select branch_id, sum(fee_amount_usd) as total_fee from main.finance_core.fee_revenue group by 1 order by 2 desc limit 5"
```

The helper rewrites canonical names like `main.finance_core.fee_revenue` or `finance_core.fee_revenue` to physical SQLite tables such as `finance_core__fee_revenue`.

## Working rule

For the current 10-task milestone, use `sqlite_query.py` for local gold-SQL checks before reaching for raw SQLite table names.
