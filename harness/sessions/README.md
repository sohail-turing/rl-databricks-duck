# Sessions

Per-run state. Each run gets a directory:

```
sessions/
  <run_id>/
    trace.jsonl          # tool calls, SQL run, assets touched
    output/              # the agent's output artifacts (per-run namespaced)
    score.json           # final verifier result
    timing.json          # latency / token counts
```

The reset script removes any artifacts the agent wrote outside this dir.

Contents are git-ignored.
