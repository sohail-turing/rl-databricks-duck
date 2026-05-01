# Harness

This folder is the future automation layer for running tasks against an agent tool surface.

## Current status

`harness/runner.py` is still a scaffold and currently raises `NotImplementedError`.

That means the harness is not the primary day-to-day loop for the current 10-task milestone.

Current working milestone loop:

1. author the task in the repo
2. validate the gold SQL locally against SQLite
3. run the manual or Genie-style 3-pass smoke check outside the unfinished harness path

## Current folder layout

```text
harness/
  runner.py
  ablation/
  sessions/
```

## What this folder is meant to own later

1. the tool surface the agent sees
2. the baseline agent wiring
3. per-run namespaced outputs
4. ablation apply/undo execution
5. run orchestration for suites and claims

## Team guidance right now

Do not present the harness as production-ready automation yet. For the current milestone, treat it as planned infrastructure, not finished operating tooling.
