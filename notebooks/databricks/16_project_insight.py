# Databricks notebook source
# MAGIC %md
# MAGIC # 16 · Project Insight (capstone)
# MAGIC *Raw feed to governed, monitored briefings, with a runbook for 3 a.m.*
# MAGIC
# MAGIC Everything you built comes together. This notebook is the **health check** you would schedule as the last
# MAGIC task of `shield_daily`: it raises an error (and so triggers your alert) when the platform looks wrong.
# MAGIC Read `docs/runbook.md` for what to do when it fails.

# COMMAND ----------

from datetime import datetime, timedelta

from pyspark.sql import functions as F

problems: list[str] = []


def check(name: str, ok: bool, detail: str) -> None:
    print(("PASS " if ok else "FAIL ") + name + " — " + detail)
    if not ok:
        problems.append(name)


# COMMAND ----------

# MAGIC %md ## 1. Reconciliation: nothing lost between layers

# COMMAND ----------

bronze_ids = spark.table("shield.bronze.incident_reports").select("incident_id").distinct().count()
silver_n = spark.table("shield.silver.incident_reports").count()
quarantine_ids = spark.table("shield.silver.incident_reports_quarantine").select("incident_id").distinct().count()
check("reconciliation", silver_n + quarantine_ids >= bronze_ids * 0.99, f"bronze={bronze_ids} silver={silver_n} quarantine={quarantine_ids}")

# COMMAND ----------

# MAGIC %md ## 2. Quality: quarantine rate within tolerance

# COMMAND ----------

rate = quarantine_ids / max(bronze_ids, 1)
check("quarantine_rate", rate < 0.15, f"{rate:.1%} of incidents quarantined (limit 15%)")

# COMMAND ----------

# MAGIC %md ## 3. Freshness: gold was updated recently

# COMMAND ----------

last = spark.sql("DESCRIBE HISTORY shield.gold.daily_threat_briefing").agg(F.max("timestamp")).first()[0]
age = datetime.now(last.tzinfo) - last
check("gold_freshness", age < timedelta(days=1), f"gold last written {age} ago")

# COMMAND ----------

# MAGIC %md ## 4. Uniqueness: no duplicate keys in silver

# COMMAND ----------

dupes = spark.sql("SELECT COUNT(*) FROM (SELECT incident_id FROM shield.silver.incident_reports GROUP BY 1 HAVING COUNT(*) > 1)").first()[0]
check("silver_unique", dupes == 0, f"{dupes} duplicated incident_ids")

# COMMAND ----------

# MAGIC %md ## 5. Cost and operations (system tables)
# MAGIC Requires a metastore admin to enable the `billing` and `lakeflow` system schemas.

# COMMAND ----------

try:
    display(
        spark.sql(
            """
            SELECT usage_date, sku_name, ROUND(SUM(usage_quantity), 2) AS dbus
            FROM system.billing.usage
            WHERE usage_date >= current_date() - INTERVAL 14 DAYS
            GROUP BY ALL ORDER BY usage_date DESC, dbus DESC LIMIT 20
            """
        )
    )
    display(
        spark.sql(
            """
            SELECT job_id, result_state, COUNT(*) AS runs
            FROM system.lakeflow.job_run_timeline
            WHERE period_start_time >= current_timestamp() - INTERVAL 7 DAYS
            GROUP BY ALL ORDER BY runs DESC LIMIT 20
            """
        )
    )
except Exception as e:  # noqa: BLE001
    print("System tables unavailable (enable the schemas first):", type(e).__name__)

# COMMAND ----------

# Fail the task so the job's failure notification fires.
if problems:
    raise RuntimeError(f"Project Insight health check failed: {problems}")
print("All checks passed.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Break each check on purpose (e.g. delete a bronze file's rows) and confirm the failure message tells you where to look.
# MAGIC 2. Write the 5-minute walkthrough of this platform: sources, layers, quality, orchestration, governance, cost, failure handling.
# MAGIC 3. Add a check for schema drift (a new column in bronze that silver does not know about).
