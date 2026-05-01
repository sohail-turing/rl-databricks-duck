# Verification

This folder holds current local validation artifacts and the placeholders for later statistical verification outputs.

## Current layout

```text
verification/
  runs/                  # local SQLite artifacts and later automated run outputs
  exports/               # CSV exports from the generator
  schema/                # JSON schema exports from the generator
  reports/               # later claim-verification reports
  coverage.md            # later taxonomy coverage output
```

## What is active now

| Area | Current use |
| --- | --- |
| `runs/` | stores `tier_a_seed.sqlite`, `tier_b_seed.sqlite`, and `tier_c_seed.sqlite` |
| `exports/` | stores the team-facing CSV export folders |
| `schema/` | stores JSON schema exports for the generated tables |
| `reports/` | reserved for later verified-claim reports |

## Current milestone verification posture

1. local data validation is active now through SQLite, CSV, and JSON schema outputs
2. task smoke runs are currently a 3-attempt process outside the unfinished harness path
3. anchors and distractors are manual for this first 10-task milestone
4. full statistical claim verification is a later phase, not the current delivery gate

## Later full verification flow

When the broader verification layer is active, it will follow the Fisher's-exact workflow described in `validator.md` and implemented by `tools/stats.py`.
