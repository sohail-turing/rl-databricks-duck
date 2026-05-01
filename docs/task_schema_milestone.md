# Milestone Task Schema

This document freezes the working task shape for the first 10-task milestone.

It is based on:

1. `tasks/_example.yaml`
2. `tasks/_template.yaml`
3. `validator.md` section 7

The purpose of this note is not to replace the long-term schema. It is to keep the first milestone stable while allowing small field changes later without rewriting the whole batch.

---

## 1. Base format

Each task should stay in the existing YAML shape used by the repo.

Required top-level fields for this milestone:

1. `id`
2. `domain`
3. `sub_domain`
4. `difficulty`
5. `target_pass_at_5`
6. `query`
7. `minimal_hint`
8. `expected_assets`
9. `gold_sql`
10. `gold_answer`
11. `verifier`
12. `distractors`
13. `anchors`
14. `output_location`

This keeps the first 10 tasks compatible with the sample task structure already in the repo.

---

## 2. Milestone-specific domain values

For this milestone, the primary task domain should be one of:

1. `finance`
2. `hr`
3. `communication`
4. `marketing`
5. `operations`

`operations` should be used only when the task is primarily operational. For cross-domain tasks, choose the dominant analytical surface as the primary `domain` and capture the other surfaces through `sub_domain`, `expected_assets`, and the task description.

---

## 3. Difficulty mapping

Use the existing difficulty bands:

1. `easy`
2. `medium`
3. `hard`

Use the following `target_pass_at_5` values:

1. easy: `">80%"`
2. medium: `"20-80%"`
3. hard: `"<20%"`

---

## 4. Field guidance

### `id`

Use milestone-friendly IDs:

1. `T-001` to `T-010`

### `sub_domain`

Keep this business-specific and useful for routing. Examples:

1. `gl`
2. `deposits`
3. `payroll`
4. `employee_directory`
5. `incident_threads`
6. `campaigns`
7. `branch_operations`

### `query`

The query should sound like a realistic analyst request inside a bank workspace.

### `minimal_hint`

For this milestone:

1. hard tasks should always include a real minimal hint
2. easy and medium tasks can keep a short placeholder hint if not needed yet

If a task does not really need a hint yet, keep the field present and use a short neutral placeholder rather than deleting it.

### `expected_assets`

This should enumerate only the assets the gold path actually relies on.

It may include:

1. tables
2. notebooks
3. dashboards
4. drive docs

### `gold_sql`

This must run successfully against the milestone workspace slice.

### `gold_answer`

For the first 10 tasks, prefer programmatic answer types where possible:

1. `number`
2. `string`
3. `set`
4. `table`

### `verifier`

Default choice for the milestone:

1. `kind: programmatic`
2. `spec: numeric_match`, `exact_match`, or `set_match`

Use judge rubrics only if a task genuinely needs open-ended scoring.

---

## 5. Anchor and distractor policy for the first milestone

This milestone is still in the manual-claim stage.

That means:

1. every distractor and anchor stays in the same list structure as the sample schema
2. `verified` must remain `false`
3. `notes` should explain the intended manual role when needed
4. `ablation` can still be recorded as the intended method, but it should not be presented as fully validated yet

A distractor from one task may be reused as an anchor in another task if that improves coherence.

---

## 6. Recommended default skeleton

```yaml
id: T-001
domain: finance
sub_domain: deposits
difficulty: medium
target_pass_at_5: "20-80%"
query: |
  ...
minimal_hint: |
  ...
expected_assets:
  tables: []
  notebooks: []
  dashboards: []
  drive_docs: []
gold_sql: |
  ...
gold_answer:
  type: number
  value: 0
  tolerance: 0
  accepted_formats: []
verifier:
  kind: programmatic
  spec: numeric_match
  rubric: ""
distractors: []
anchors: []
output_location: "/Workspace/Users/${eval_user}/_runs/${run_id}/T-001/"
```

---

## 7. Freeze rule for this week

The working shape above is now the Phase 0 baseline.

If additional feedback changes the task definition later, only the changed fields should be patched. The first 10 tasks should not be rewritten into a different format unless there is a hard blocker.