# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · First recon
# MAGIC *Your first look at the raw feeds.*
# MAGIC
# MAGIC You will generate the seed data into a volume and explore it with DataFrames and SQL.
# MAGIC Run on **serverless** compute (notebook compute dropdown) to keep things simple.
# MAGIC
# MAGIC **How to run:** connect serverless compute, then **Run all**.
# MAGIC
# MAGIC **Needs:** chapter 01 done (the volume `shield.landing.staging` must exist).
# MAGIC
# MAGIC **What happens:** a generator in `src/shield_data` writes synthetic S.H.I.E.L.D. data (incident reports with 5% deliberate defects, agents,
# MAGIC locations, sensor pings) as files into the volume. You then read the files and explore them. Safe to re-run: the fixed seed rewrites the same files.

# COMMAND ----------

# MAGIC %md
# MAGIC `generate(...)` is our own helper (imported from the repo). It writes files to the volume `staging`, split into 5 batches per feed so they can
# MAGIC "arrive one at a time" in chapter 03. **Expect:** a dictionary with the number of rows per feed.

# COMMAND ----------

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..", "..", "src")))
from shield_data.generate import generate

STAGING = Path("/Volumes/shield/landing/staging")

# 10k incidents, 5% dirty, split into 5 files per feed (they "arrive" one at a time in chapter 03)
counts = generate(STAGING, incidents=10_000, pings=20_000, seed=42, dirty=0.05, batches=5)
counts

# COMMAND ----------

# MAGIC %md ## A DataFrame is a lazy plan
# MAGIC Nothing below reads data until an **action** (`display`, `count`, `write`) runs.

# COMMAND ----------

# MAGIC %md
# MAGIC `spark.read.json(folder)` reads all JSON files in the folder into one DataFrame. Spark guesses the column types by reading the data
# MAGIC (*schema inference*): fine here, slow and fragile for real data. `printSchema()` shows the result. **Expect:** a list of columns such as `incident_id`, `severity`, `reported_at`.

# COMMAND ----------

from pyspark.sql import functions as F

incidents = spark.read.json(f"{STAGING}/incident_reports")
incidents.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC A first look at 10 rows. `limit` keeps it cheap. Nothing was really read until this line: a DataFrame is a *plan*, and `display` is an *action* that runs it.

# COMMAND ----------

display(incidents.limit(10))

# COMMAND ----------

# MAGIC %md ## Transformations

# COMMAND ----------

# MAGIC %md
# MAGIC `groupBy` + `agg` counts incidents and sums casualties per type and severity. `orderBy(desc("n"))` puts the biggest groups first.
# MAGIC These are *transformations* (lazy). `display` triggers the work. Grouping moves data between machines (a *shuffle*), which is where time goes in Spark.

# COMMAND ----------

by_type = (
    incidents.groupBy("incident_type", "severity")
    .agg(F.count("*").alias("n"), F.sum("casualties").alias("casualties"))
    .orderBy(F.desc("n"))
)
display(by_type)

# COMMAND ----------

# MAGIC %md ## The same thing in SQL

# COMMAND ----------

# MAGIC %md
# MAGIC The same question in SQL. A **temp view** gives a DataFrame a table name that exists only in this notebook session.
# MAGIC **Expect:** exactly the same numbers as above. DataFrame code and SQL are the same engine; pick whichever reads better.

# COMMAND ----------

incidents.createOrReplaceTempView("incidents_tmp")
display(
    spark.sql(
        """
        SELECT incident_type, severity, COUNT(*) AS n, SUM(casualties) AS casualties
        FROM incidents_tmp
        GROUP BY incident_type, severity
        ORDER BY n DESC
        """
    )
)

# COMMAND ----------

# MAGIC %md ## Spot the mess
# MAGIC The generator injected defects. Find them before the quality chapters do.

# COMMAND ----------

# MAGIC %md
# MAGIC Three quick checks for the defects the generator injected: missing `agent_id`, invalid `severity` values, and duplicate `incident_id`s.
# MAGIC Write down what you find; chapters 05 and 06 deal with each.

# COMMAND ----------

display(incidents.filter(F.col("agent_id").isNull()).limit(5))
display(incidents.groupBy("severity").count())
display(incidents.groupBy("incident_id").count().filter("count > 1").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Join incidents with `agents/agents.csv` and list the five busiest codenames.
# MAGIC 2. Use `explain()` on `by_type` and find the shuffle (`Exchange`) in the plan.
# MAGIC 3. How many incidents have a `reported_at` that is not a valid timestamp?
