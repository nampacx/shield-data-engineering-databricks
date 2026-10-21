# Databricks notebook source
# MAGIC %md
# MAGIC # 07 · Doctor Strange's time stone
# MAGIC *"Which version of this record was true last Tuesday?"*
# MAGIC
# MAGIC Delta keeps a versioned log of every change. You will tamper with a table (Hydra!), see exactly what changed,
# MAGIC and restore it. Needs chapter 06's `shield.silver.incident_reports`.
# MAGIC
# MAGIC **How to run:** connect serverless compute and run the cells **in order, one at a time** so you can see each state.
# MAGIC
# MAGIC **Needs:** chapter 06 done (`shield.silver.incident_reports`).
# MAGIC
# MAGIC **What happens:** a story in six steps. You switch on the change data feed, let "Hydra" tamper with the table, find out what changed and who did it,
# MAGIC read the old version of the data, and restore it. If the run stops after the tampering and before `RESTORE`, run the `RESTORE` cell yourself.

# COMMAND ----------

# MAGIC %md
# MAGIC `T` is just the table name stored in a Python variable, so the SQL below can use `{T}` (f-strings).

# COMMAND ----------


T = "shield.silver.incident_reports"

# COMMAND ----------

# MAGIC %md ## Turn on the change data feed

# COMMAND ----------

# MAGIC %md
# MAGIC `delta.enableChangeDataFeed = true` makes Delta record row-level changes from now on. We also note the current **version** number: that is our known-good state.
# MAGIC **Expect:** `Known-good version: <number>`.

# COMMAND ----------

spark.sql(f"ALTER TABLE {T} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")
good_version = spark.sql(f"DESCRIBE HISTORY {T}").first()["version"]
print("Known-good version:", good_version)

# COMMAND ----------

# MAGIC %md ## Hydra tampers: downgrade critical incidents

# COMMAND ----------

# MAGIC %md
# MAGIC The attack: every `critical` incident is downgraded to `low`. **Expect:** the severity counts show no `critical` any more. In real life nobody would notice this in a dashboard.

# COMMAND ----------

spark.sql(f"UPDATE {T} SET severity = 'low' WHERE severity = 'critical'")
display(spark.sql(f"SELECT severity, COUNT(*) AS n FROM {T} GROUP BY severity"))

# COMMAND ----------

# MAGIC %md ## Audit: what changed, when, and by whom?

# COMMAND ----------

# MAGIC %md
# MAGIC `DESCRIBE HISTORY` is a free audit log: each version with timestamp, **who** ran it, which operation, and metrics such as rows updated. The `UPDATE` is the newest row.

# COMMAND ----------

display(spark.sql(f"DESCRIBE HISTORY {T}").select("version", "timestamp", "userName", "operation", "operationMetrics"))

# COMMAND ----------

# MAGIC %md ### Row-level view with the change data feed

# COMMAND ----------

# MAGIC %md
# MAGIC The **change data feed** shows *which rows* changed. `_change_type` is `update_preimage` (before) or `update_postimage` (after). We query everything after the known-good version.
# MAGIC **Expect:** counts per change type and a sample of the old values.

# COMMAND ----------

changes = spark.sql(f"SELECT * FROM table_changes('{T}', {good_version + 1})")
display(changes.groupBy("_change_type").count())
display(changes.filter("_change_type = 'update_preimage'").select("incident_id", "severity").limit(5))

# COMMAND ----------

# MAGIC %md ## Time travel: read the past

# COMMAND ----------

# MAGIC %md
# MAGIC **Time travel:** `VERSION AS OF n` reads the table as it was at version n. **Expect:** the original severity counts, including `critical`. The current table is still tampered.

# COMMAND ----------

before = spark.sql(f"SELECT severity, COUNT(*) AS n FROM {T} VERSION AS OF {good_version} GROUP BY severity")
display(before)

# COMMAND ----------

# MAGIC %md ## Undo it

# COMMAND ----------

# MAGIC %md
# MAGIC `RESTORE` rolls the table back to the known-good version. **Expect:** `critical` rows are back.

# COMMAND ----------

spark.sql(f"RESTORE TABLE {T} TO VERSION AS OF {good_version}")
display(spark.sql(f"SELECT severity, COUNT(*) AS n FROM {T} GROUP BY severity"))

# COMMAND ----------

# MAGIC %md `RESTORE` is itself a new version, so the tampering stays visible in the history. Nothing is erased.

# COMMAND ----------

# MAGIC %md
# MAGIC `RESTORE` is itself a new version, so the whole story (tamper, restore) stays visible in the history. Nothing is erased. Time travel is not a backup, though: `VACUUM` eventually removes old files.

# COMMAND ----------

display(spark.sql(f"DESCRIBE HISTORY {T}").select("version", "operation").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Use `TIMESTAMP AS OF` instead of a version number.
# MAGIC 2. Use the change feed to build `silver.incident_audit` (incident_id, old severity, new severity, changed_at).
# MAGIC 3. What happens to time travel after `VACUUM ... RETAIN 0 HOURS`? Try it on a throwaway table only.
