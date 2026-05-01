# Bank Canon

This document is the Phase 0 source of truth for the first 10-task milestone.

It defines the fictional bank that anchors the first delivery so the data, tasks, and support assets all read like parts of the same business.

---

## 1. Locked identity

**Bank name:** Meridian Trust Bank  
**Type:** mid-sized regional retail and small-business bank  
**Headquarters:** Charlotte, North Carolina  
**Operating model:** branch network plus digital banking  
**Tone:** operational, regulated, customer-facing, internally collaborative

This is the identity that should be used across the first 10 tasks unless a later revision explicitly changes it.

---

## 2. Business footprint

Default business footprint for the milestone:

1. retail deposits
2. small-business checking and savings
3. cards and payment products
4. consumer lending
5. branch operations
6. digital servicing and customer acquisition

### Geographic footprint

The default branch footprint is the U.S. Southeast:

1. North Carolina
2. South Carolina
3. Georgia
4. Florida

Branches, employees, customers, campaigns, and incidents should primarily live inside this footprint unless a task explicitly needs an exception.

---

## 3. Functional domains in the milestone

| Domain | Canon meaning |
|---|---|
| Finance | ledger, fee revenue, deposits, loans, branch financial performance |
| HR | employee roster, payroll, movement, staffing structure |
| Communication | internal collaboration channels, incident discussion, campaign communication |
| Marketing | campaigns, targeting, customer acquisition, conversion |
| Operations | branch incidents, service disruptions, SLA events |

Operations is a shared operational layer rather than a full standalone business pillar for this first milestone.

---

## 4. Shared entities and ID conventions

These entities should stay stable across the first 10 tasks.

1. `customer_id`
2. `account_id`
3. `employee_id`
4. `branch_id`
5. `campaign_id`
6. `channel_id`
7. `period_id`
8. `product_id`

### ID format guidance

Use consistent human-readable prefixes:

1. `CUST-000001`
2. `ACCT-000001`
3. `EMP-000001`
4. `BR-001`
5. `CMP-0001`
6. `CH-001`
7. `2025-M01` or `2025-Q1`
8. `PRD-001`

These IDs are the glue across domains. If a table cannot join through one of these shared keys, it should be reconsidered before being added to the milestone slice.

---

## 5. Time window

Default reporting window for this milestone:

1. current year
2. previous year
3. monthly and quarterly rollups available where needed

This is enough to support trend, period-over-period, and incident-timing tasks without overcomplicating the seed set.

---

## 6. Product families and business language

Use the following product families by default:

1. retail checking
2. high-yield savings
3. small-business checking
4. consumer credit card
5. auto loan
6. personal loan

Use the following communication and campaign tone:

1. campaign names tied to deposits, cards, lending, or onboarding
2. internal channel names tied to branch operations, risk, marketing, and service recovery
3. employee roles that match a bank setting, such as branch manager, operations analyst, payroll specialist, campaign manager, and service lead

Avoid:

1. random generic business language
2. domain names or email addresses that break the bank story
3. assets that feel like they belong to a different company or industry

---

## 7. `users_pool.json` mapping guidance

The sanitized `users_pool.json` can be used as a people seed source.

Suggested mapping:

1. employee directory rows
2. communication user profiles
3. marketing audience contacts
4. limited customer-contact dimensions

Before use:

1. subset the file
2. rewrite employee emails to the bank domain, for example `firstname.lastname@meridiantrust.bank`
3. keep only the fields needed for the milestone slice
4. treat the file as seed input, not as a final exposed artifact

---

## 8. Phase 0 decisions now considered closed

The following Phase 0 decisions are now locked:

1. bank name: Meridian Trust Bank
2. primary geography: Southeastern United States
3. working shared ID set: customer, account, employee, branch, campaign, channel, period, product
4. `users_pool.json` is approved only as sanitized seed input

The remaining execution-specific items move to the milestone schema and gold-table map:

1. first 10 gold tables
2. hard-task cross-surface selection
3. asset reuse across tasks