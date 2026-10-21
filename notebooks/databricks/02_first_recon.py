# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · First recon
# MAGIC *Your first look at the raw feeds.*
# MAGIC
# MAGIC You will generate the seed data into a volume and explore it with DataFrames and SQL.
# MAGIC Run on **serverless** compute (notebook compute dropdown) to keep things simple.

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

from pyspark.sql import functions as F

incidents = spark.read.json(f"{STAGING}/incident_reports")
incidents.printSchema()

# COMMAND ----------

display(incidents.limit(10))

# COMMAND ----------

# MAGIC %md ## Transformations

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

display(incidents.filter(F.col("agent_id").isNull()).limit(5))
display(incidents.groupBy("severity").count())
display(incidents.groupBy("incident_id").count().filter("count > 1").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Join incidents with `agents/agents.csv` and list the five busiest codenames.
# MAGIC 2. Use `explain()` on `by_type` and find the shuffle (`Exchange`) in the plan.
# MAGIC 3. How many incidents have a `reported_at` that is not a valid timestamp?
