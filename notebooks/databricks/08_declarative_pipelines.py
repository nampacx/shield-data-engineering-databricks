# Databricks notebook source
# MAGIC %md
# MAGIC # 08 · Declarative pipelines
# MAGIC *Describe what each table should be and let the platform work out the how.*
# MAGIC
# MAGIC The pipeline code lives in `pipelines/shield_insight.py` (open it first). Decorators like `@dp.table` only work
# MAGIC inside a **pipeline**, so this notebook is the companion: create the pipeline, run it, then inspect results.
# MAGIC
# MAGIC ### Create the pipeline (UI)
# MAGIC 1. **Jobs & Pipelines → Create → ETL pipeline**.
# MAGIC 2. Name `shield_insight`, default catalog `shield`, default schema `pipeline`
# MAGIC    (create it first: `CREATE SCHEMA IF NOT EXISTS shield.pipeline`).
# MAGIC 3. Choose **Add existing assets** → root folder = this repo's `pipelines` folder, source file `shield_insight.py`.
# MAGIC 4. Compute: **serverless**. Add configuration `raw_path = /Volumes/shield/landing/raw`.
# MAGIC 5. **Run pipeline**. Then deliver more files with notebook 03's `deliver()` and run it again: only the new files are processed.
# MAGIC
# MAGIC **How to run:** this chapter is different. The pipeline is **created and run in the UI**; this notebook only prepares the schema and inspects the result.
# MAGIC Order: 1) run the first code cell, 2) create the pipeline (steps above), 3) run it, 4) run the remaining cells here.
# MAGIC
# MAGIC **Needs:** chapters 03 and 05 done, and raw files delivered by notebook 03 (the pipeline reads `/Volumes/shield/landing/raw`).
# MAGIC
# MAGIC **What happens:** `pipelines/shield_insight.py` declares the same bronze → silver → gold flow as chapters 03–06, but you write no checkpoints, no write logic and no ordering.
# MAGIC The platform builds the dependency graph and handles incremental processing. Quality rules are built in as *expectations*.

# COMMAND ----------

# MAGIC %md
# MAGIC Creates the schema the pipeline will write to. **Run this first**, before creating the pipeline. **Expect:** an empty table list until the pipeline has run once.

# COMMAND ----------

spark.sql("CREATE SCHEMA IF NOT EXISTS shield.pipeline")
display(spark.sql("SHOW TABLES IN shield.pipeline"))

# COMMAND ----------

# MAGIC %md ## Inspect results

# COMMAND ----------

# MAGIC %md
# MAGIC After the pipeline run: severity counts in the pipeline's silver table. Compare with chapter 06: only valid values, because the pipeline uses `expect_or_drop` rules.

# COMMAND ----------

display(spark.sql("SELECT severity, COUNT(*) AS n FROM shield.pipeline.incidents_silver GROUP BY severity"))

# COMMAND ----------

# MAGIC %md
# MAGIC The pipeline's gold table (a materialized view). It should look like chapter 05's, but it was built and refreshed by the pipeline, not by your code.

# COMMAND ----------

display(spark.sql("SELECT * FROM shield.pipeline.daily_threat_briefing ORDER BY report_date DESC LIMIT 10"))

# COMMAND ----------

# MAGIC %md ## Data quality metrics live in the pipeline event log
# MAGIC In the pipeline UI open `incidents_silver` → **Data quality** tab, or query the event log. Replace the table
# MAGIC name below with your pipeline's event log (pipeline settings → *Advanced* → event log, or the
# MAGIC `event_log(TABLE(...))` function).

# COMMAND ----------

# MAGIC %md
# MAGIC Every pipeline update writes events, including how many rows passed or failed each expectation. This query reads them. If it errors, open the pipeline in the UI,
# MAGIC click `incidents_silver` and use the **Data quality** tab instead.

# COMMAND ----------

display(
    spark.sql(
        """
        SELECT timestamp, details:flow_progress.data_quality.expectations AS expectations
        FROM event_log(TABLE(shield.pipeline.incidents_silver))
        WHERE event_type = 'flow_progress' AND details:flow_progress.data_quality IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 5
        """
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Change `expect_or_drop` to `expect` on one rule and compare the silver row counts.
# MAGIC 2. Rewrite `daily_threat_briefing` in SQL (`CREATE MATERIALIZED VIEW ...`) in a second file.
# MAGIC 3. Add a quarantine table to the pipeline: a table with the inverse of the rules.
# MAGIC 4. What happens to a materialized view when you **Full refresh** vs. a normal run?
