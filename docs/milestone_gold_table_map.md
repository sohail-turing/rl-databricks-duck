# Milestone Gold Table Map

This document defines the first-pass gold-table plan for the 10-task milestone.

It is the bridge between the bank canon and the actual task set.

The goal here is not to list every possible table. The goal is to identify the smallest coherent set of authoritative tables that can support the first 10 tasks.

---

## 1. Shared authoritative dimensions

These tables should be treated as the common authoritative dimensions for the milestone slice.

| Table | Purpose | Key columns |
|---|---|---|
| `main.certified.customers` | customer identity and segmentation | `customer_id`, `branch_id`, `product_id`, `signup_date` |
| `main.certified.accounts` | account-level entity used by deposits and conversions | `account_id`, `customer_id`, `branch_id`, `product_id`, `account_open_date` |
| `main.certified.employees` | employee identity and reporting structure | `employee_id`, `branch_id`, `department`, `manager_id` |
| `main.certified.branches` | branch and region lookup | `branch_id`, `branch_name`, `region_name`, `state_code` |
| `main.certified.calendar_periods` | shared reporting periods | `period_id`, `start_date`, `end_date`, `period_type` |
| `main.certified.products` | bank product catalog | `product_id`, `product_family`, `product_name` |
| `main.certified.channels` | communication and campaign channels | `channel_id`, `channel_name`, `channel_type` |

---

## 2. Domain gold tables

### Finance

| Table | Purpose | Join path |
|---|---|---|
| `main.finance_gl.gl_entries` | ledger and booked financial impact | `period_id`, `branch_id`, optional `account_id` |
| `main.finance_core.fee_revenue` | branch and product fee performance | `branch_id`, `product_id`, `period_id` |
| `main.finance_core.deposit_balances` | account and branch deposit balance facts | `account_id`, `customer_id`, `branch_id`, `period_id` |
| `main.finance_core.loan_accounts` | lending facts and account state | `account_id`, `customer_id`, `branch_id`, `product_id`, `period_id` |

### HR

| Table | Purpose | Join path |
|---|---|---|
| `main.hr_people.employee_directory` | workforce profile and branch assignment | `employee_id`, `branch_id` |
| `main.hr_payroll.payroll_runs` | payroll facts by employee and period | `employee_id`, `period_id` |
| `main.hr_people.employee_changes` | role, manager, department, hire, exit changes | `employee_id`, `period_id`, `branch_id` |

### Communication

| Table | Purpose | Join path |
|---|---|---|
| `main.communication_threads.channel_messages` | general internal message activity | `channel_id`, `employee_id`, `period_id` |
| `main.communication_threads.incident_threads` | incident-specific discussion threads | `channel_id`, `branch_id`, `period_id` |
| `main.communication_threads.campaign_announcements` | internal marketing launch or product communication | `campaign_id`, `channel_id`, `period_id` |

### Marketing

| Table | Purpose | Join path |
|---|---|---|
| `main.marketing_campaigns.campaigns` | campaign definitions and owners | `campaign_id`, `product_id`, `period_id` |
| `main.marketing_campaigns.campaign_targets` | customer targeting facts | `campaign_id`, `customer_id`, `product_id`, `branch_id` |
| `main.marketing_attribution.lead_conversions` | conversion outcome tied to campaigns and accounts | `campaign_id`, `customer_id`, `account_id`, `period_id` |

### Operations

| Table | Purpose | Join path |
|---|---|---|
| `main.ops_branch.branch_incidents` | operational issues by branch and period | `branch_id`, `period_id`, `channel_id` |
| `main.ops_branch.service_sla_events` | SLA timing and service recovery metrics | `branch_id`, `period_id`, optional `incident_id` |

---

## 3. First-pass task-to-gold-table mapping

| Task | Primary gold table(s) | Expected joins |
|---|---|---|
| `T-001` | `main.finance_core.fee_revenue` | `fee_revenue -> branches -> calendar_periods` |
| `T-002` | `main.hr_people.employee_directory` | `employee_directory -> branches` |
| `T-003` | `main.marketing_campaigns.campaigns` | `campaigns -> products -> calendar_periods` |
| `T-004` | `main.hr_payroll.payroll_runs`, `main.finance_core.fee_revenue` | `payroll_runs -> employees -> branches`, `fee_revenue -> branches -> periods` |
| `T-005` | `main.marketing_campaigns.campaigns`, `main.marketing_attribution.lead_conversions`, `main.certified.accounts` | `campaigns -> lead_conversions -> accounts` |
| `T-006` | `main.communication_threads.incident_threads`, `main.ops_branch.branch_incidents` | `incident_threads -> branch_incidents -> branches -> periods` |
| `T-007` | `main.communication_threads.channel_messages`, `main.hr_people.employee_directory` | `channel_messages -> employees -> branches or onboarding cohort logic` |
| `T-008` | `main.ops_branch.service_sla_events`, `main.finance_core.deposit_balances` | `service_sla_events -> branches -> deposit_balances -> periods` |
| `T-009` | `main.marketing_campaigns.campaigns`, `main.communication_threads.campaign_announcements`, `main.marketing_attribution.lead_conversions` | `campaigns -> announcements -> lead_conversions -> accounts` |
| `T-010` | `main.hr_people.employee_changes`, `main.ops_branch.branch_incidents`, `main.finance_gl.gl_entries` or `main.finance_core.fee_revenue` | `employee_changes -> branches`, `branch_incidents -> branches`, finance impact by branch and period |

---

## 4. Join rules that should not drift

These rules should stay fixed across the first milestone.

1. branch-level joins go through `branch_id`
2. customer/account joins go through `customer_id` and `account_id`
3. time comparisons go through `period_id` or explicit date windows from `calendar_periods`
4. campaign reasoning goes through `campaign_id`
5. internal communication reasoning goes through `channel_id` and then to `branch_id`, `campaign_id`, or `employee_id`

If a planned task cannot be explained through one of these join rules, it is probably trying to do too much for the first milestone.

---

## 5. Exact seed order for the milestone slice

This is the recommended build order for the first milestone.

The rule is simple: seed shared dimensions first, then the easiest gold surfaces, then the cross-domain tables needed for medium and hard tasks.

### Wave 0 — Shared dimensions and lookup tables

These should be built first because nearly every task depends on them.

| Order | Table | Why it comes first | Unlocks |
|---|---|---|---|
| 1 | `main.certified.calendar_periods` | time windows and period filters are used everywhere | all tasks |
| 2 | `main.certified.branches` | branch and region joins are central to Finance and Operations | T-001, T-002, T-004, T-006, T-008, T-010 |
| 3 | `main.certified.products` | needed for campaign and product-level finance views | T-003, T-005, T-009 |
| 4 | `main.certified.channels` | needed before communication tables can be seeded cleanly | T-006, T-007, T-009 |
| 5 | `main.certified.employees` | needed by HR and communication surfaces | T-002, T-004, T-007, T-010 |
| 6 | `main.certified.customers` | needed for campaigns, conversions, deposits, and account joins | T-005, T-008, T-009 |
| 7 | `main.certified.accounts` | needed before balances and conversion facts feel coherent | T-005, T-008, T-009 |

### Wave 1 — First gold tables for easy tasks

These are the first fact tables to build because they unlock the easiest task surfaces and establish confidence quickly.

| Order | Table | Why now | Unlocks |
|---|---|---|---|
| 8 | `main.finance_core.fee_revenue` | simplest Finance gold surface; low dependency fan-out | T-001, T-004 |
| 9 | `main.hr_people.employee_directory` | simplest HR gold surface | T-002, T-007 |
| 10 | `main.marketing_campaigns.campaigns` | simplest Marketing gold surface | T-003, T-005, T-009 |

### Wave 2 — Medium-task joins

These come next because they introduce the first meaningful multi-table reasoning without overloading the build.

| Order | Table | Why now | Unlocks |
|---|---|---|---|
| 11 | `main.hr_payroll.payroll_runs` | needed for the first HR + Finance comparison task | T-004 |
| 12 | `main.marketing_attribution.lead_conversions` | needed for campaign-to-account outcome tasks | T-005, T-009 |
| 13 | `main.communication_threads.incident_threads` | needed for operational incident reasoning | T-006 |
| 14 | `main.ops_branch.branch_incidents` | pairs with incident discussions and later hard tasks | T-006, T-010 |
| 15 | `main.communication_threads.channel_messages` | needed for employee communication behavior tasks | T-007 |
| 16 | `main.finance_core.deposit_balances` | needed for branch service impact on deposit performance | T-008 |
| 17 | `main.ops_branch.service_sla_events` | completes the service-impact task path | T-008 |

### Wave 3 — Hard-task surfaces

These are only needed after the easy and medium path is already stable.

| Order | Table | Why now | Unlocks |
|---|---|---|---|
| 18 | `main.communication_threads.campaign_announcements` | connects internal comms to campaign timing | T-009 |
| 19 | `main.hr_people.employee_changes` | needed for staffing and operational-shift reasoning | T-010 |
| 20 | `main.finance_gl.gl_entries` | final finance impact layer for the hardest operational task | T-010 |

### Wave 4 — Optional later tables

These are useful, but not required for the first authoring pass.

1. `main.finance_core.loan_accounts`
2. `main.marketing_campaigns.campaign_targets`

These should only be added if they are needed by a specific task or if a distractor pattern requires them.

---

## 6. First gold-table build list

The first build list should be treated as the minimum authoritative slice that must exist before serious task authoring begins.

### Tier A — Must exist before any task drafting

1. `main.certified.calendar_periods`
2. `main.certified.branches`
3. `main.certified.products`
4. `main.certified.channels`
5. `main.certified.employees`
6. `main.certified.customers`
7. `main.certified.accounts`
8. `main.finance_core.fee_revenue`
9. `main.hr_people.employee_directory`
10. `main.marketing_campaigns.campaigns`

### Tier B — Must exist before medium-task authoring is complete

1. `main.hr_people.departments`
2. `main.hr_people.job_roles`
3. `main.hr_people.employee_assignments`
4. `main.hr_people.reporting_lines`
5. `main.hr_people.time_off_requests`
6. `main.hr_people.performance_reviews`
7. `main.hr_people.onboarding_cases`
8. `main.hr_payroll.employee_compensation_history`
9. `main.hr_payroll.payroll_runs`
10. `main.hr_benefits.benefit_plans`
11. `main.hr_benefits.benefit_enrollments`
12. `main.marketing_attribution.lead_conversions`
13. `main.communication_threads.incident_threads`
14. `main.ops_branch.branch_incidents`
15. `main.communication_threads.channel_messages`
16. `main.finance_core.deposit_balances`
17. `main.ops_branch.service_sla_events`

### Tier C — Must exist before hard-task authoring is complete

1. `main.communication_threads.campaign_announcements`
2. `main.hr_people.employee_changes`
3. `main.finance_gl.gl_entries`

This gives a clear stopping rule:

1. finish Tier A before writing more than the first three tasks
2. finish Tier B before locking the medium set
3. finish Tier C before finalizing the two hard tasks

---

## 7. Suggested build checkpoints

Use these checkpoints during Phase 1 and Phase 2.

### Checkpoint 1 — Easy-task ready

Required tables:

1. all Wave 0 tables
2. `main.finance_core.fee_revenue`
3. `main.hr_people.employee_directory`
4. `main.marketing_campaigns.campaigns`

Expected unlocked tasks:

1. T-001
2. T-002
3. T-003

### Checkpoint 2 — Medium-task ready

Required tables:

1. all Wave 1 tables
2. all Wave 2 tables

Expected unlocked tasks:

1. T-004
2. T-005
3. T-006
4. T-007
5. T-008

### Checkpoint 3 — Hard-task ready

Required tables:

1. all Wave 3 tables

Expected unlocked tasks:

1. T-009
2. T-010

---

## 8. Next use of this file

This file should now be used for:

1. deciding the exact seed order
2. deciding which tables are mandatory before each task band is written
3. assigning gold tables to each task
4. deciding which distractor assets are worth creating around them
5. deciding where cross-task anchor/distractor reuse makes sense
