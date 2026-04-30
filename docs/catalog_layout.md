# Catalog Layout

> Unity Catalog structure. Every schema in the workspace must fall into exactly one tier of the trust hierarchy.
> Status: **stub — to be filled during WS-1**.

## Schema-trust hierarchy

```
Tier 1 — Gold standard
  main.certified.*

Tier 2 — Maintained metrics
  main.metric_store.*

Tier 2b — Materialization backing tables (DO NOT QUERY DIRECTLY)
  main.metric_store_internal.*

Tier 3 — Team raw data
  main.sales_<sub>.*
  main.marketing_<sub>.*
  main.finance_<sub>.*
  main.eng_<sub>.*

Tier 4 — Scratch
  main.tmp.*

Tier 5 — Personal scratch
  users.<person>.*
```

The agent's expected priority order is **Tier 1 > Tier 2 > Tier 3 > Tier 4 > Tier 5**.
`Tier 2b` is never authoritative — it exists only as a high-fidelity distractor.

## Schema list (initial)

> To be expanded during WS-1.

| Schema                              | Tier | Domain     | Notes                                      |
| ----------------------------------- | ---- | ---------- | ------------------------------------------ |
| `main.certified`                    | 1    | (all)      | The gold tables.                           |
| `main.metric_store`                 | 2    | (all)      | Maintained marts.                          |
| `main.metric_store_internal`        | 2b   | (all)      | Backing tables — `fct__*__<hash>`.         |
| `main.sales_orders`                 | 3    | Sales      | Raw order data.                            |
| `main.sales_pipeline`               | 3    | Sales      | CRM pipeline data.                         |
| `main.marketing_campaigns`          | 3    | Marketing  | Campaign event logs.                       |
| `main.marketing_attribution`        | 3    | Marketing  | Attribution model output.                  |
| `main.marketing_web_analytics`      | 3    | Marketing  | Web events.                                |
| `main.finance_gl`                   | 3    | Finance    | General ledger.                            |
| `main.finance_ar`                   | 3    | Finance    | Accounts receivable.                       |
| `main.finance_ap`                   | 3    | Finance    | Accounts payable.                          |
| `main.eng_servicedesk`              | 3    | Engineering| Ticket data.                               |
| `main.eng_asset_management`         | 3    | Engineering| IT asset registry.                         |
| `main.eng_procurement`              | 3    | Engineering| Procurement orders. **(includes deprecated tables)** |
| `main.tmp`                          | 4    | (any)      | Scratch.                                   |
| `users.<person>`                    | 5    | (any)      | Personal scratch — generated per persona.  |
