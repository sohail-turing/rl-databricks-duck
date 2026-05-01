# Sessions

This folder is reserved for per-run harness state once automated runs are wired.

## Current milestone status

The current 10-task milestone does not yet write active run state here because the harness runner is still scaffolded.

## Expected later layout

```text
sessions/
  <run_id>/
    trace.jsonl
    output/
    score.json
    timing.json
```

When the harness becomes live, this folder should hold namespaced run artifacts and remain git-ignored.
