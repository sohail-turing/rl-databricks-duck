# Meridian Trust 10-Task Milestone

This repo currently supports the first Meridian Trust Bank milestone: a SQLite-first local data slice, support assets, task templates, and the scaffolding for later harness and verification expansion.

The broad long-horizon Databricks program documents are still here, but the team should treat the 10-task bank slice as the operational focus for current work.

## Start here

1. `10_task_plan.md` — current milestone workflow, ERD, commands, and delivery gates.
2. `phase3_context.md` — low-token handoff for task authoring.
3. `docs/bank_canon.md` — locked Meridian Trust Bank identity and naming rules.
4. `docs/milestone_schema_map.md` — minimum schema and joins.
5. `docs/milestone_gold_table_map.md` — gold paths and table build order.
6. `workspace/generators/README.md` — generator commands and local artifact flow.

## Current working artifacts

| Artifact | Path | Purpose |
| --- | --- | --- |
| Local SQLite database | `verification/runs/tier_c_seed.sqlite` | Main local source of truth for task authoring |
| CSV export | `verification/exports/tier_c_csv/` | Easy table review for the team |
| JSON schema export | `verification/schema/tier_c_json/` | Portable schema handoff |
| Canonical local SQL helper | `tools/sqlite_query.py` | Query SQLite with canonical table names |

## Common local commands

```bash
cd /Users/apple/Documents/turing/apple/databrick-rl

# Rebuild the Tier C milestone slice
.venv/bin/python -m workspace.generators.run \
  --target sqlite \
  --build tier-c \
  --out verification/runs/tier_c_seed.sqlite \
  --csv-dir verification/exports/tier_c_csv \
  --schema-json-dir verification/schema/tier_c_json

# Inspect canonical-to-SQLite mappings
.venv/bin/python tools/sqlite_query.py --list-mapping

# Run local SQL with canonical table names
.venv/bin/python tools/sqlite_query.py --sql "select branch_id, sum(fee_amount_usd) as total_fee from main.finance_core.fee_revenue group by 1 order by 2 desc limit 5"
```

## Repo layout

| Path | Current role |
| --- | --- |
| `docs/` | Bank canon, schema maps, task guidance, and runbooks |
| `workspace/` | Generators, manifests, notebooks, dashboard placeholders, and drive docs |
| `tasks/` | Milestone task templates and future task specs |
| `verifier/` | Programmatic matchers plus judge scaffolding |
| `harness/` | Future automation layer; currently still scaffolded |
| `verification/` | SQLite runs, CSV exports, JSON schemas, and later report outputs |
| `tools/` | Helper scripts for local querying, validation, and coverage |

## Current status

1. Phase 0, Phase 1, and Phase 2 are complete.
2. Phase 3 task authoring is ready to proceed on top of the SQLite artifact.
3. The generator, CSV export, JSON schema export, and canonical local SQL helper are working now.
4. The harness, judge runner, and statistical ablation flow are still partial scaffolds and should not be presented as finished automation yet.
