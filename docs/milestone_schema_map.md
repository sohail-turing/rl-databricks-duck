# Milestone Schema Map

This document defines the minimal schema needed to support the first 10 tasks.

It is intentionally small. The goal is to make the first milestone coherent and buildable, not to simulate the full long-term workspace yet.

---

## 1. Trust-tiered schema layout for the milestone

| Schema | Tier | Role in the milestone |
|---|---|---|
| `main.certified` | Tier 1 | shared authoritative dimensions and lookup tables |
| `main.finance_core` | Tier 3 | primary Finance facts used by the milestone tasks |
| `main.finance_gl` | Tier 3 | booked finance impact for the hardest operational task |
| `main.hr_people` | Tier 3 | employee profile and change history |
| `main.hr_payroll` | Tier 3 | payroll and compensation facts |
| `main.hr_benefits` | Tier 3 | benefit plan and enrollment facts |
| `main.communication_threads` | Tier 3 | internal communication and incident discussion surfaces |
| `main.marketing_campaigns` | Tier 3 | campaign definitions and targeting |
| `main.marketing_attribution` | Tier 3 | conversion facts tied to campaigns and accounts |
| `main.ops_branch` | Tier 3 | branch incidents and SLA events |
| `main.metric_store_internal` | Tier 2b | high-fidelity backing-table distractors when needed |
| `main.tmp` | Tier 4 | scratch-schema distractors |
| `users.<person>` | Tier 5 | personal-space distractors |

For this milestone, some authoritative task surfaces live in domain schemas rather than only in `main.certified`. That is acceptable as long as the gold path is documented clearly and the task points to the right authoritative table.

---

## 2. Shared authoritative dimension layer

These tables should exist before any serious task authoring starts.

### `main.certified.calendar_periods`

Minimum columns:

1. `period_id`
2. `period_type`
3. `start_date`
4. `end_date`
5. `fiscal_year`

### `main.certified.branches`

Minimum columns:

1. `branch_id`
2. `branch_name`
3. `region_name`
4. `state_code`
5. `market_name`

### `main.certified.products`

Minimum columns:

1. `product_id`
2. `product_name`
3. `product_family`
4. `product_group`

### `main.certified.channels`

Minimum columns:

1. `channel_id`
2. `channel_name`
3. `channel_type`
4. `business_owner`

### `main.certified.employees`

Minimum columns:

1. `employee_id`
2. `employee_name`
3. `branch_id`
4. `department`
5. `manager_id`
6. `hire_date`
7. `employment_type`
8. `email`

### `main.certified.customers`

Minimum columns:

1. `customer_id`
2. `customer_name`
3. `branch_id`
4. `product_id`
5. `signup_date`
6. `segment`
7. `state_code`

### `main.certified.accounts`

Minimum columns:

1. `account_id`
2. `customer_id`
3. `branch_id`
4. `product_id`
5. `account_open_date`
6. `account_status`
7. `current_balance_usd`

---

## 3. Finance schema map

### `main.finance_core.fee_revenue`

Purpose: branch and product fee performance

Minimum columns:

1. `branch_id`
2. `product_id`
3. `period_id`
4. `fee_type`
5. `fee_amount_usd`

### `main.finance_core.deposit_balances`

Purpose: account and branch balance movement

Minimum columns:

1. `account_id`
2. `customer_id`
3. `branch_id`
4. `period_id`
5. `ending_balance_usd`
6. `average_balance_usd`

### `main.finance_core.loan_accounts`

Purpose: lending state and balance context

Minimum columns:

1. `account_id`
2. `customer_id`
3. `branch_id`
4. `product_id`
5. `period_id`
6. `loan_status`
7. `outstanding_principal_usd`

### `main.finance_gl.gl_entries`

Purpose: booked finance impact and branch-level ledger signals

Minimum columns:

1. `period_id`
2. `branch_id`
3. `account_id`
4. `gl_account_code`
5. `amount_usd`
6. `entry_type`

---

## 4. HR schema map

### `main.hr_people.employee_directory`

Purpose: branch-assigned workforce profile

Minimum columns:

1. `employee_id`
2. `branch_id`
3. `department`
4. `role_title`
5. `manager_id`
6. `employment_status`

### Expanded HR analytics layer

Purpose: connected workforce graph for realistic HR analytics, inspired by HRIS/payroll systems such as Deel

Tables:

1. `main.hr_people.departments` — department dimension and executive owner
2. `main.hr_people.job_roles` — role, job family, level, and salary-band dimension
3. `main.hr_people.employee_assignments` — employee, branch, department, role, manager, cost center, FTE, and work-location assignment
4. `main.hr_people.reporting_lines` — direct manager graph over employees
5. `main.hr_people.time_off_requests` — leave requests tied to employee, manager, branch, and period
6. `main.hr_people.performance_reviews` — employee review outcomes tied to manager, branch, period, payroll signal, and branch pressure
7. `main.hr_people.onboarding_cases` — new-hire case status tied to employee, manager, HR partner, branch, and period
8. `main.hr_payroll.employee_compensation_history` — monthly compensation snapshots tied to payroll, role, department, cost center, branch, and period
9. `main.hr_benefits.benefit_plans` — benefit plan dimension
10. `main.hr_benefits.benefit_enrollments` — employee benefit enrollment facts

### `main.hr_payroll.payroll_runs`

Purpose: payroll facts by employee and period

Minimum columns:

1. `employee_id`
2. `period_id`
3. `branch_id`
4. `base_pay_usd`
5. `bonus_pay_usd`
6. `total_pay_usd`

### `main.hr_people.employee_changes`

Purpose: staffing movement and structural changes

Minimum columns:

1. `employee_id`
2. `period_id`
3. `branch_id`
4. `change_type`
5. `old_department`
6. `new_department`
7. `effective_date`

---

## 5. Communication schema map

### `main.communication_threads.channel_messages`

Purpose: general internal communication activity

Minimum columns:

1. `channel_id`
2. `employee_id`
3. `period_id`
4. `message_ts`
5. `message_type`
6. `engagement_count`

### `main.communication_threads.incident_threads`

Purpose: incident-specific discussion and escalation

Minimum columns:

1. `channel_id`
2. `branch_id`
3. `period_id`
4. `incident_id`
5. `thread_ts`
6. `severity`
7. `message_count`

### `main.communication_threads.campaign_announcements`

Purpose: internal campaign-launch communication

Minimum columns:

1. `campaign_id`
2. `channel_id`
3. `period_id`
4. `announcement_ts`
5. `owner_employee_id`
6. `announcement_type`

---

## 6. Marketing schema map

### `main.marketing_campaigns.campaigns`

Purpose: campaign definitions and ownership

Minimum columns:

1. `campaign_id`
2. `product_id`
3. `period_id`
4. `campaign_name`
5. `campaign_channel`
6. `budget_usd`
7. `owner_employee_id`

### `main.marketing_campaigns.campaign_targets`

Purpose: targeting facts for customers and products

Minimum columns:

1. `campaign_id`
2. `customer_id`
3. `product_id`
4. `branch_id`
5. `target_segment`

### `main.marketing_attribution.lead_conversions`

Purpose: campaign-to-account conversion facts

Minimum columns:

1. `campaign_id`
2. `customer_id`
3. `account_id`
4. `period_id`
5. `conversion_status`
6. `conversion_ts`
7. `booked_revenue_usd`

---

## 7. Operations schema map

### `main.ops_branch.branch_incidents`

Purpose: branch-level disruptions and operational incidents

Minimum columns:

1. `incident_id`
2. `branch_id`
3. `period_id`
4. `channel_id`
5. `incident_type`
6. `severity`
7. `opened_ts`
8. `resolved_ts`

### `main.ops_branch.service_sla_events`

Purpose: service-response and recovery timing

Minimum columns:

1. `sla_event_id`
2. `branch_id`
3. `period_id`
4. `incident_id`
5. `response_minutes`
6. `resolution_minutes`
7. `sla_breached_flag`

---

## 8. Join backbone

These joins should stay stable across the milestone:

1. `customers.customer_id -> accounts.customer_id`
2. `accounts.branch_id -> branches.branch_id`
3. `employees.branch_id -> branches.branch_id`
4. `fee_revenue.branch_id -> branches.branch_id`
5. `deposit_balances.account_id -> accounts.account_id`
6. `payroll_runs.employee_id -> employees.employee_id`
7. `campaigns.product_id -> products.product_id`
8. `lead_conversions.account_id -> accounts.account_id`
9. `incident_threads.incident_id -> branch_incidents.incident_id`
10. `branch_incidents.branch_id -> branches.branch_id`
11. `service_sla_events.incident_id -> branch_incidents.incident_id`
12. `channel_messages.channel_id -> channels.channel_id`
13. `campaign_announcements.campaign_id -> campaigns.campaign_id`
14. all fact tables that are time-based should join to `calendar_periods.period_id`

---

## 9. First build rule

The first milestone should be built in this order:

1. shared dimensions
2. easy-task gold tables
3. medium-task join tables
4. hard-task support tables
5. optional distractor-only tables only after the gold path is stable

This schema map should be read together with `docs/milestone_gold_table_map.md`.
