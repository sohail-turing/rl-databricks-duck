# Harness

Runs tasks. Owns:

- The **tool surface** the agent sees (SQL exec, list catalogs / schemas / tables, get table metadata, read notebook, read dashboard query, MCP retrieve).
- The **baseline agent** wired to that surface (frontier model — Claude / GPT-class — used for both eval and verification ablations).
- **Per-run namespaced output dirs** so concurrent runs don't collide.
- **Ablation apply/undo scripts** under `ablation/T-XXX/<claim_id>/` — used by WS-9 verification.
- **Reset script** that removes per-run artifacts after scoring.

## Components

```
harness/
  __init__.py
  runner.py              # CLI: --task, --suite, --concurrency, --ablation
  tools/                 # Databricks tool surface
    __init__.py
    sql.py
    catalog.py
    notebooks.py
    dashboards.py
    drive_mcp.py
  agent/                 # baseline agent wired to the tool surface
    __init__.py
    frontier.py          # OpenAI / Anthropic / etc.
  ablation/              # paired apply/undo scripts per (task, claim)
  sessions/              # per-run state
```

To be filled during WS-8.
