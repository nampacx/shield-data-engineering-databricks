# Databricks notebook source
# MAGIC %md
# MAGIC # 07 · Doctor Strange's time stone
# MAGIC *"Which version of this record was true last Tuesday?"*
# MAGIC
# MAGIC Delta keeps a versioned log of every change. You will tamper with a table (Hydra!), see exactly what changed,
# MAGIC and restore it. Needs chapter 06's `shield.silver.incident_reports`.

# COMMAND ----------


T = "shield.silver.incident_reports"

# COMMAND ----------

# MAGIC %md ## Turn on the change data feed

# COMMAND ----------

spark.sql(f"ALTER TABLE {T} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")
good_version = spark.sql(f"DESCRIBE HISTORY {T}").first()["version"]
print("Known-good version:", good_version)

# COMMAND ----------

# MAGIC %md ## Hydra tampers: downgrade critical incidents

# COMMAND ----------

spark.sql(f"UPDATE {T} SET severity = 'low' WHERE severity = 'critical'")
display(spark.sql(f"SELECT severity, COUNT(*) AS n FROM {T} GROUP BY severity"))

# COMMAND ----------

# MAGIC %md ## Audit: what changed, when, and by whom?

# COMMAND ----------

display(spark.sql(f"DESCRIBE HISTORY {T}").select("version", "timestamp", "userName", "operation", "operationMetrics"))

# COMMAND ----------

# MAGIC %md ### Row-level view with the change data feed

# COMMAND ----------

changes = spark.sql(f"SELECT * FROM table_changes('{T}', {good_version + 1})")
display(changes.groupBy("_change_type").count())
display(changes.filter("_change_type = 'update_preimage'").select("incident_id", "severity").limit(5))

# COMMAND ----------

# MAGIC %md ## Time travel: read the past

# COMMAND ----------

before = spark.sql(f"SELECT severity, COUNT(*) AS n FROM {T} VERSION AS OF {good_version} GROUP BY severity")
display(before)

# COMMAND ----------

# MAGIC %md ## Undo it

# COMMAND ----------

spark.sql(f"RESTORE TABLE {T} TO VERSION AS OF {good_version}")
display(spark.sql(f"SELECT severity, COUNT(*) AS n FROM {T} GROUP BY severity"))

# COMMAND ----------

# MAGIC %md `RESTORE` is itself a new version, so the tampering stays visible in the history. Nothing is erased.

# COMMAND ----------

display(spark.sql(f"DESCRIBE HISTORY {T}").select("version", "operation").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Use `TIMESTAMP AS OF` instead of a version number.
# MAGIC 2. Use the change feed to build `silver.incident_audit` (incident_id, old severity, new severity, changed_at).
# MAGIC 3. What happens to time travel after `VACUUM ... RETAIN 0 HOURS`? Try it on a throwaway table only.
