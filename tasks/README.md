# Tasks

This folder holds the formal task specs for the Meridian Trust milestone.

## Current milestone target

The active delivery target is the first 10 tasks:

1. `T-001` to `T-003`
2. `T-004` to `T-008`
3. `T-009` and `T-010`

Working difficulty mix:

1. 3 easy
2. 5 medium
3. 2 hard

## Current contents

| File or folder | Purpose |
| --- | --- |
| `_template.yaml` | Starting shape for each new task |
| `_example.yaml` | Reference task showing the expected field structure |
| `rubrics/` | Judge rubrics when a task needs LLM-as-judge scoring |

## Current authoring loop

1. start from `tasks/_template.yaml`
2. use `phase3_context.md` and `10_task_plan.md` for the current workflow
3. run local gold SQL against `verification/runs/tier_c_seed.sqlite`
4. prefer canonical names locally through `tools/sqlite_query.py`
5. capture the exact gold answer before saving the task file
6. keep anchors and distractors manual for this milestone

## Current milestone rules

1. do not mark `verified: true` on anchors or distractors
2. prefer programmatic verifiers where possible
3. only include notebooks or drive docs in `expected_assets` if the gold path really depends on them

See `docs/add_a_task.md` and `docs/task_schema_milestone.md` for the detailed field rules.
