# Milestone Asset Reuse Map

This document defines the first-pass asset reuse and distractor plan for the 10-task milestone.

The goal is to make the first 10 tasks coherent and economical:

1. reuse the same assets where that improves realism
2. avoid inventing a fresh support surface for every task
3. identify early where one task's distractor can become another task's anchor

---

## 1. Reuse principles

1. Gold tables should be reused across related tasks whenever the business question overlaps naturally.
2. Communication and operational assets are especially useful as cross-task supporting evidence.
3. A support asset should only be reused if its role is still believable in the new task.
4. Manual anchor and distractor roles must be documented honestly; they are not statistically verified yet.

---

## 2. Planned cross-task reuse decisions

These are the most valuable reuse patterns for the first milestone.

| Asset | Role in one task | Role in another task | Why this reuse works |
|---|---|---|---|
| `main.communication_threads.campaign_announcements` | distractor candidate for `T-003` | anchor candidate for `T-009` | not authoritative for a pure campaign KPI question, but useful for campaign launch timing in a hard cross-surface task |
| `main.ops_branch.branch_incidents` | distractor candidate for `T-008` | gold or anchor for `T-006` and `T-010` | incident counts are the wrong grain for SLA impact, but the right surface for disruption analysis |
| `main.communication_threads.channel_messages` | distractor candidate for `T-006` | anchor or gold for `T-007` | general channel chatter is noisy for incident resolution, but correct for announcement engagement |
| `main.finance_core.fee_revenue` | gold for `T-001` | anchor for `T-004` and possible support for `T-010` | stable branch-level finance surface reused across multiple questions |
| `main.hr_people.employee_directory` | gold for `T-002` | anchor for `T-007` | canonical employee profile surface reused in workforce and communication analysis |

---

## 3. Per-task first-pass asset plan

| Task | Gold assets | Candidate distractor assets | Planned reuse note |
|---|---|---|---|
| `T-001` | `main.finance_core.fee_revenue` | `main.metric_store_internal.fct__fee_revenue__a83f2c1`, `main.tmp.branch_fee_revenue`, `users.analyst.fee_revenue_qtd` | `main.finance_core.fee_revenue` should later support `T-004` |
| `T-002` | `main.hr_people.employee_directory`, `main.certified.branches` | `main.hr_people.employee_directory_old`, `users.people.employee_list_v2`, `main.tmp.employee_snapshot` | `main.hr_people.employee_directory` should later support `T-007` |
| `T-003` | `main.marketing_campaigns.campaigns`, `main.certified.products` | `main.communication_threads.campaign_announcements`, `main.metric_store_internal.fct__campaigns__b91a2d7e`, `users.marketing.campaign_snapshot` | `campaign_announcements` should later become useful in `T-009` |
| `T-004` | `main.hr_payroll.payroll_runs`, `main.finance_core.fee_revenue`, `main.certified.branches` | `main.hr_people.employee_directory` as wrong-grain shortcut, `main.tmp.payroll_summary`, `users.finance.branch_margin_export` | reuse `fee_revenue` from `T-001` |
| `T-005` | `main.marketing_campaigns.campaigns`, `main.marketing_attribution.lead_conversions`, `main.certified.accounts` | `main.marketing_campaigns.campaign_targets`, `users.marketing.lead_export_final`, `main.tmp.account_openings_rollup` | conversion surfaces should also support `T-009` |
| `T-006` | `main.communication_threads.incident_threads`, `main.ops_branch.branch_incidents` | `main.communication_threads.channel_messages`, `main.tmp.incident_activity`, `users.ops.outage_notes` | `branch_incidents` should later support `T-010` |
| `T-007` | `main.communication_threads.channel_messages`, `main.hr_people.employee_directory` | `main.communication_threads.incident_threads`, `users.hr.onboarding_notes`, `main.tmp.employee_engagement` | reuses `employee_directory` from `T-002` and `channel_messages` from `T-006` |
| `T-008` | `main.ops_branch.service_sla_events`, `main.finance_core.deposit_balances`, `main.certified.branches` | `main.ops_branch.branch_incidents`, `main.tmp.service_metrics`, `users.finance.deposit_outage_check` | `branch_incidents` is intentionally a distractor here but remains useful elsewhere |
| `T-009` | `main.marketing_campaigns.campaigns`, `main.communication_threads.campaign_announcements`, `main.marketing_attribution.lead_conversions` | `main.marketing_campaigns.campaign_targets`, `users.marketing.launch_notes`, `main.tmp.campaign_roi` | explicit distractor-to-anchor reuse from `T-003` |
| `T-010` | `main.hr_people.employee_changes`, `main.ops_branch.branch_incidents`, `main.finance_gl.gl_entries` | `main.finance_core.fee_revenue` as incomplete finance shortcut, `users.ops.staffing_tracker`, `main.tmp.branch_change_log` | reuses `branch_incidents` from `T-006` and finance support from `T-001` |

---

## 4. First distractor clusters worth building

These are the distractor patterns most worth building early because they can be reused across multiple tasks.

### Cluster A — Finance metric copies

1. `main.metric_store_internal.fct__fee_revenue__<hash>`
2. `main.tmp.branch_fee_revenue`
3. `users.<person>.fee_revenue_qtd`

Useful for:

1. `T-001`
2. `T-004`
3. `T-010`

### Cluster B — HR snapshots and stale exports

1. `main.hr_people.employee_directory_old`
2. `main.tmp.employee_snapshot`
3. `users.<person>.employee_list_v2`

Useful for:

1. `T-002`
2. `T-007`

### Cluster C — Marketing and announcement lookalikes

1. `main.communication_threads.campaign_announcements`
2. `main.metric_store_internal.fct__campaigns__<hash>`
3. `users.<person>.campaign_snapshot`

Useful for:

1. `T-003`
2. `T-005`
3. `T-009`

### Cluster D — Incident and SLA confusion surfaces

1. `main.ops_branch.branch_incidents`
2. `main.ops_branch.service_sla_events`
3. `main.communication_threads.channel_messages`

Useful for:

1. `T-006`
2. `T-008`
3. `T-010`

---

## 5. Manual claim handling note

For this milestone:

1. these reuse assignments are design-time decisions, not validated claims
2. `verified` should remain `false` in the task files
3. the role of a reused asset should be described clearly in `notes`
4. if a reused asset stops being believable in a later task draft, drop the reuse rather than force it

---

## 6. Next use of this file

This file should be used for:

1. deciding which distractor assets are worth seeding first
2. avoiding duplicate support assets during the first 10 tasks
3. planning which cross-task reuse patterns to preserve during task writing
4. identifying at least one clear distractor-to-anchor reuse example for the milestone