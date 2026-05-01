# Databricks notebook source
# MAGIC %md
# MAGIC # Meridian Trust staffing change watch
# MAGIC
# MAGIC This notebook is used to inspect branch staffing shifts alongside incident pressure
# MAGIC and booked finance impact.

# COMMAND ----------

STAFFING_CHANGE_WATCH_SQL = """
SELECT
  ec.branch_id,
  ec.period_id,
  ec.employee_id,
  ec.change_type,
  ec.old_department,
  ec.new_department,
  bi.incident_id,
  gl.gl_account_code,
  gl.amount_usd,
  gl.entry_type
FROM hr_people.employee_changes ec
LEFT JOIN ops_branch.branch_incidents bi
  ON bi.branch_id = ec.branch_id
 AND bi.period_id = ec.period_id
LEFT JOIN finance_gl.gl_entries gl
  ON gl.branch_id = ec.branch_id
 AND gl.period_id = ec.period_id
ORDER BY ec.period_id DESC, ec.branch_id, ec.employee_id
"""