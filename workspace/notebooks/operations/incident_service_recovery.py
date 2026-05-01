# Databricks notebook source
# MAGIC %md
# MAGIC # Meridian Trust incident service recovery review
# MAGIC
# MAGIC This notebook captures the operational path from branch incidents to SLA recovery
# MAGIC metrics and deposit balance movement.

# COMMAND ----------

INCIDENT_SERVICE_RECOVERY_SQL = """
SELECT
  bi.branch_id,
  bi.period_id,
  bi.incident_id,
  bi.severity,
  sla.response_minutes,
  sla.resolution_minutes,
  sla.sla_breached_flag,
  db.ending_balance_usd,
  db.average_balance_usd
FROM ops_branch.branch_incidents bi
JOIN ops_branch.service_sla_events sla
  ON sla.incident_id = bi.incident_id
LEFT JOIN finance_core.deposit_balances db
  ON db.branch_id = bi.branch_id
 AND db.period_id = bi.period_id
ORDER BY bi.period_id DESC, bi.branch_id, bi.incident_id
"""