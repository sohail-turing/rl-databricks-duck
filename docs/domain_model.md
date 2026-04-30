# Domain Model

> Canonical entities, the **common entity pool**, and the relationships between them.
> This is the source-of-truth for every generator in `workspace/generators/`.
> Locked on Day 1 of W1 (WS-1).

## 1. The common entity pool

The cross-cutting entities below form a **single canonical pool** that lives in `main.certified.*` and is referenced by every domain. Any analytical question that crosses domain boundaries (e.g. "what's the AR balance of my top-5 sales customers in Q1?") relies on this pool. See `plan.md` §0.1 for the design rationale.

### Pool entities

| Entity                | Catalog.schema.table                       | Approx rows  | Owner generator                                |
| --------------------- | ------------------------------------------ | ------------ | ---------------------------------------------- |
| `customers`           | `main.certified.customers`                 | ~10,000      | `generators/customers.py`                      |
| `organisations`       | `main.certified.organisations`             | ~2,000       | `generators/organisations.py`                  |
| `products`            | `main.certified.products`                  | ~500         | `generators/products.py`                       |
| `employees`           | `main.certified.employees`                 | ~5,000       | `generators/employees.py`                      |
| `financial_periods`   | `main.certified.financial_periods`         | 12 quarters  | `generators/financial_periods.py`              |
| `currencies`          | `main.certified.currencies`                | ~50          | `generators/currencies.py`                     |
| `fx_rates`            | `main.certified.fx_rates`                  | daily × ccy  | `generators/fx_rates.py`                       |
| `cost_centers`        | `main.certified.cost_centers`              | ~100         | `generators/cost_centers.py`                   |
| `geographies`         | `main.certified.geographies`               | countries + regions + cities | `generators/geographies.py`     |

### Pool entity columns (locked Day 1)

#### `customers`
- `customer_id` (STRING, PK)
- `customer_name` (STRING)
- `organisation_id` (STRING, FK → `organisations`)
- `email` (STRING)
- `signup_date` (DATE)
- `region_id` (STRING, FK → `geographies`)
- `tier` (STRING — `enterprise`, `mid_market`, `smb`)
- `lifecycle_stage` (STRING — `prospect`, `active`, `churned`)
- `account_owner_id` (STRING, FK → `employees`)
- `cost_center_code` (STRING, FK → `cost_centers`)

#### `organisations`
- `organisation_id` (STRING, PK)
- `organisation_name` (STRING)
- `parent_organisation_id` (STRING, FK self-ref, nullable)
- `industry` (STRING)
- `headquarters_country_code` (STRING, FK → `geographies`)
- `employee_count_band` (STRING)
- `annual_revenue_band` (STRING)
- `tier` (STRING)

#### `products`
- `product_id` (STRING, PK)
- `product_name` (STRING)
- `product_family` (STRING)
- `sku` (STRING)
- `list_price_usd` (DECIMAL)
- `currency_code` (STRING, FK → `currencies`)
- `launched_date` (DATE)
- `lifecycle_stage` (STRING — `ga`, `beta`, `eol`)

#### `employees`
- `employee_id` (STRING, PK)
- `employee_name` (STRING)
- `email` (STRING)
- `manager_id` (STRING, FK self-ref, nullable)
- `department` (STRING)
- `cost_center_code` (STRING, FK → `cost_centers`)
- `office_location_id` (STRING, FK → `geographies`)
- `hire_date` (DATE)
- `role_title` (STRING)
- `is_active` (BOOLEAN)

#### `financial_periods`
- `period_id` (STRING, PK — e.g. `2026-Q1`, `2026-M01`)
- `period_type` (STRING — `quarter`, `month`, `year`)
- `start_date` (DATE)
- `end_date` (DATE)
- `fiscal_year` (INT)
- `is_current` (BOOLEAN)

#### `currencies`
- `currency_code` (STRING, PK — `USD`, `EUR`, `GBP`, …)
- `currency_name` (STRING)
- `symbol` (STRING)

#### `fx_rates`
- `as_of_date` (DATE)
- `from_currency_code` (STRING, FK → `currencies`)
- `to_currency_code` (STRING, FK → `currencies`)
- `rate` (DECIMAL)
- PK: (`as_of_date`, `from_currency_code`, `to_currency_code`)

#### `cost_centers`
- `cost_center_code` (STRING, PK)
- `cost_center_name` (STRING)
- `department` (STRING)
- `parent_cost_center_code` (STRING, FK self-ref, nullable)
- `owner_employee_id` (STRING, FK → `employees`)

#### `geographies`
- `geo_id` (STRING, PK)
- `geo_type` (STRING — `country`, `region`, `city`)
- `geo_name` (STRING)
- `parent_geo_id` (STRING, FK self-ref, nullable)
- `country_code` (STRING — ISO-3166)

## 2. Domains and sub-domains

| Domain       | Sub-domains                                       |
| ------------ | ------------------------------------------------- |
| Sales        | `orders`, `accounts`, `pipeline`                  |
| Marketing    | `campaigns`, `attribution`, `web_analytics`       |
| Finance      | `gl`, `ar`, `ap`                                  |
| Engineering  | `servicedesk`, `asset_management`, `procurement`  |

## 3. Domain fact tables — FK contracts into the pool

Every domain fact table carries the appropriate FK columns into the pool. Examples:

### Sales

| Table                                        | Pool FKs (`*_id`)                                                                     |
| -------------------------------------------- | ------------------------------------------------------------------------------------- |
| `main.sales_orders.orders`                   | `customer_id`, `organisation_id`, `product_id`, `employee_id` (sales rep), `period_id`, `currency_code` |
| `main.sales_pipeline.opportunities`          | `customer_id`, `organisation_id`, `product_id`, `employee_id` (owner), `period_id`     |
| `main.sales_pipeline.leads`                  | `organisation_id`, `employee_id` (sdr), `region_id`                                    |

### Marketing

| Table                                        | Pool FKs                                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------- |
| `main.marketing_campaigns.campaigns`         | `product_id`, `period_id`, `region_id`, `employee_id` (campaign owner)                |
| `main.marketing_attribution.attributions`    | `customer_id`, `campaign_id`, `period_id`                                              |
| `main.marketing_web_analytics.web_events`    | `customer_id` (nullable — anonymous), `period_id`                                      |

### Finance

| Table                                        | Pool FKs                                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------- |
| `main.finance_gl.gl_entries`                 | `cost_center_code`, `period_id`, `currency_code`, `organisation_id`                   |
| `main.finance_ar.ar_invoices`                | `customer_id`, `organisation_id`, `period_id`, `currency_code`                         |
| `main.finance_ap.ap_invoices`                | `organisation_id` (vendor), `cost_center_code`, `period_id`, `currency_code`           |

### Engineering

| Table                                        | Pool FKs                                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------- |
| `main.eng_servicedesk.tickets`               | `employee_id` (reporter), `employee_id` (assignee), `period_id`, `cost_center_code`    |
| `main.eng_asset_management.it_assets`        | `employee_id` (assignee), `cost_center_code`, `office_location_id` (FK → geographies)  |
| `main.eng_procurement.purchase_orders`       | `organisation_id` (vendor), `cost_center_code`, `period_id`, `currency_code`           |

## 4. Coherence rules (locked Day 1)

- **Pool first.** WS-2a loads the pool before any domain fact table runs (WS-2b).
- **Same RNG seed** drives every generator → IDs are deterministic across runs.
- **Referential integrity ≥ 95%** on every FK — small noise tail allowed for realism (orphan IDs that look like data-quality issues).
- **Time coherence**: every fact table draws from `financial_periods` so `WHERE period_id = '2026-Q1'` resolves identically across domains.
- **FX coherence**: every monetary column is paired with a `currency_code`; any conversion to USD goes through `fx_rates`.
- **One canonical customer**: every `customer_id` in any domain exists in `main.certified.customers`.
- **One canonical employee**: every `employee_id` in any domain exists in `main.certified.employees`.
- **Workspace covers ~3 fiscal years** (12 quarters in `financial_periods`).

## 5. Cross-domain join smoke test (Day 5 acceptance)

The Day 5 cross-domain join smoke test runs a query of the shape:

```sql
SELECT
    c.tier,
    p.period_id,
    SUM(o.total_usd)        AS sales_usd,
    SUM(ar.balance_usd)     AS ar_balance_usd,
    COUNT(t.ticket_id)      AS open_tickets
FROM main.certified.customers           c
JOIN main.certified.financial_periods   p   ON p.is_current = TRUE
LEFT JOIN main.sales_orders.orders      o   ON o.customer_id     = c.customer_id     AND o.period_id  = p.period_id
LEFT JOIN main.finance_ar.ar_invoices   ar  ON ar.customer_id    = c.customer_id     AND ar.period_id = p.period_id
LEFT JOIN main.eng_servicedesk.tickets  t   ON t.organisation_id = c.organisation_id AND t.period_id  = p.period_id AND t.status = 'OPEN'
GROUP BY c.tier, p.period_id;
```

The smoke test passes if:
- The query executes against Unity Catalog without error.
- ≥ 95% of `customer_id`s in `orders`, `ar_invoices`, and `tickets` resolve in `customers`.
- The result has at least one non-null row per customer tier.

## 6. Open items (lock during Day 1)

- [ ] Lock the row-count for each pool entity (above are working approximations).
- [ ] Lock the time window covered (default: 3 fiscal years).
- [ ] Decide whether `customers` and `employees` carry an `is_pii_redacted` flag.
- [ ] Decide whether `fx_rates` is daily or month-end.
