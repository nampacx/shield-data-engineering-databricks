# Databricks notebook source
# MAGIC %md
# MAGIC # 10 · Maria Hill schedules
# MAGIC *Hill does not run things by hand.*
# MAGIC
# MAGIC This is a **job task notebook**: parameterised, idempotent, and safe to retry. You build a Lakeflow Job with
# MAGIC three tasks (`ingest → silver → gold`) that each run this notebook with a different `step`.
# MAGIC The same job is defined as code in chapter 13.
# MAGIC
# MAGIC ### Create the job (UI)
# MAGIC 1. **Jobs & Pipelines → Create → Job**. Name `shield_daily`.
# MAGIC 2. Task `ingest`: type *Notebook*, this notebook, parameter `step=ingest`. Compute: serverless.
# MAGIC 3. Task `silver`: `step=silver`, depends on `ingest`. Task `gold`: `step=gold`, depends on `silver`.
# MAGIC 4. Set **Retries = 2** on each task, add a failure **notification**, add a schedule (start it *paused*).
# MAGIC 5. **Run now**, then run again: results must be identical (idempotency).
# MAGIC
# MAGIC **How to run (by hand first):** connect serverless compute, run the first code cell so the `step` dropdown appears, pick `ingest`, then run the cells below it (cell menu → **Run All Below**). Repeat with `silver`, then `gold`.
# MAGIC Afterwards build the job (steps above) so these three runs happen automatically.
# MAGIC
# MAGIC **Needs:** chapters 03 to 06 done (bronze incidents, `silver.locations`, quality rules).
# MAGIC
# MAGIC **What happens:** the same notebook does a different job depending on the `step` widget. That is how one notebook becomes three job tasks. Each step is **idempotent**: running it twice gives the same result, so retries are safe.

# COMMAND ----------

# MAGIC %md
# MAGIC Setup plus two widgets. `step` (dropdown: `ingest`, `silver`, `gold`) selects what to do. `deliver_files` (text, default `1`) says how many raw files the ingest step copies in. In a job, you set these as task parameters instead of clicking.
# MAGIC Run this cell, pick a step in the dropdown, then run the rest.

# COMMAND ----------

import os
import shutil
import sys
from pathlib import Path

from pyspark.sql import Window
from pyspark.sql import functions as F

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..", "..", "src")))
from shield_data.quality import INCIDENT_RULES

dbutils.widgets.dropdown("step", "ingest", ["ingest", "silver", "gold"], "Pipeline step")
dbutils.widgets.text("deliver_files", "1", "Files to deliver (ingest step only)")

# COMMAND ----------

# MAGIC %md
# MAGIC Pick the `step` in the dropdown above, then run the cell below to read it. (In a job, the task parameter sets it for you.)

# COMMAND ----------

step = dbutils.widgets.get("step")

STAGING, RAW = Path("/Volumes/shield/landing/staging"), Path("/Volumes/shield/landing/raw")
CP = "/Volumes/shield/landing/checkpoints"
TS = "yyyy-MM-dd'T'HH:mm:ss'Z'"

# COMMAND ----------

# MAGIC %md
# MAGIC **Step `ingest`:** copies the next undelivered file(s) into `raw` (files already there are skipped = idempotent), then loads new files into bronze with Auto Loader, as in chapter 03.

# COMMAND ----------

# MAGIC %md
# MAGIC **Step `silver`:** applies the quality rules, keeps the latest valid row per incident and writes silver, and writes failures to quarantine (chapter 06). It **overwrites** the tables from bronze, so repeating it changes nothing.

# COMMAND ----------

# MAGIC %md
# MAGIC **Step `gold`:** rebuilds the daily briefing table from silver. Also a full replace, so safe to repeat.

# COMMAND ----------

# MAGIC %md
# MAGIC This line picks the function that matches the widget value and runs it. **Expect:** `step '<name>' done`. In the job run page, a green task means this line printed without an error.

# COMMAND ----------


def step_ingest() -> None:
    # Simulated delivery. Idempotent: files already delivered are skipped.
    feed = "incident_reports"
    (RAW / feed).mkdir(parents=True, exist_ok=True)
    have = {p.name for p in (RAW / feed).glob("*")}
    for p in [p for p in sorted((STAGING / feed).glob("*")) if p.name not in have][: int(dbutils.widgets.get("deliver_files"))]:
        shutil.copy(p, RAW / feed / p.name)
    (
        spark.readStream.format("cloudFiles").option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", f"{CP}/{feed}/schema")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load(f"{RAW}/{feed}")
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_ingested_at", F.current_timestamp())
        .writeStream.option("checkpointLocation", f"{CP}/{feed}/checkpoint").option("mergeSchema", "true")
        .trigger(availableNow=True).toTable("shield.bronze.incident_reports")
    )


def step_silver() -> None:
    parsed = spark.table("shield.bronze.incident_reports").withColumn("reported_ts", F.expr(f'try_to_timestamp(reported_at, "{TS}")'))
    failed = F.array(*[F.when(F.coalesce(F.expr(e), F.lit(False)), F.lit(None)).otherwise(F.lit(n)) for n, e in INCIDENT_RULES.items()])
    checked = parsed.withColumn("failed_rules", F.filter(failed, lambda x: x.isNotNull()))
    latest = Window.partitionBy("incident_id").orderBy(F.col("_ingested_at").desc())
    (  # Full overwrite derived from bronze: running it twice gives the same result.
        checked.filter(F.size("failed_rules") == 0).drop("failed_rules")
        .withColumn("rn", F.row_number().over(latest)).filter("rn = 1").drop("rn")
        .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("shield.silver.incident_reports")
    )
    (
        checked.filter(F.size("failed_rules") > 0).withColumn("_quarantined_at", F.current_timestamp())
        .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("shield.silver.incident_reports_quarantine")
    )


def step_gold() -> None:
    spark.sql(
        """
        CREATE OR REPLACE TABLE shield.gold.daily_threat_briefing AS
        SELECT CAST(i.reported_ts AS DATE) AS report_date, l.city, l.country, i.incident_type, i.severity,
               COUNT(*) AS incidents, SUM(i.casualties) AS casualties
        FROM shield.silver.incident_reports i JOIN shield.silver.locations l USING (location_id)
        GROUP BY ALL
        """
    )


{"ingest": step_ingest, "silver": step_silver, "gold": step_gold}[step]()
print(f"step '{step}' done")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Make the job fail on purpose (rename a table), confirm the notification, then fix it and **Repair run**.
# MAGIC 2. Add a task-level *condition*: only run `gold` if `silver` produced more than 0 rows.
# MAGIC 3. Replace the `silver` full overwrite with an incremental `MERGE`. What must stay true for retries to be safe?
