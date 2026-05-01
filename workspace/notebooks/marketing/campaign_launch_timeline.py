# Databricks notebook source
# MAGIC %md
# MAGIC # Meridian Trust campaign launch timeline
# MAGIC
# MAGIC This notebook is a lightweight discovery surface for campaign launch timing,
# MAGIC internal announcement sequence, and downstream conversion follow-through.

# COMMAND ----------

CAMPAIGN_LAUNCH_TIMELINE_SQL = """
SELECT
  c.campaign_id,
  c.campaign_name,
  c.period_id,
  c.campaign_channel,
  a.announcement_type,
  a.announcement_ts,
  lc.conversion_status,
  lc.booked_revenue_usd
FROM marketing_campaigns.campaigns c
LEFT JOIN communication_threads.campaign_announcements a
  ON a.campaign_id = c.campaign_id
LEFT JOIN marketing_attribution.lead_conversions lc
  ON lc.campaign_id = c.campaign_id
ORDER BY c.period_id DESC, c.campaign_id, a.announcement_ts
"""