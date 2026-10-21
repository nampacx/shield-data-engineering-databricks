# Databricks notebook source
# MAGIC %md
# MAGIC # 12 · Hawkeye's precision
# MAGIC *One arrow, one target: fewer files, smarter layout, cheaper queries.*
# MAGIC
# MAGIC The default data is small, so this notebook generates **500k incidents** to make differences visible.
# MAGIC Measure with the **Query Profile** (query history → a query → *See query profile*), not with your feelings.
# MAGIC
# MAGIC **How to run:** connect serverless compute and **Run all**. The first code cell takes a while (it generates 500,000 incidents once).
# MAGIC
# MAGIC **Needs:** chapters 02 and 05 done (`shield.silver.locations`).
# MAGIC
# MAGIC **What happens:** the same data is stored two ways (plain and with **liquid clustering**) and one query is run on both. You then check, in the **Query Profile**, how many files each query could skip.
# MAGIC Remember to drop the demo tables at the end.

# COMMAND ----------

# MAGIC %md
# MAGIC Generates a bigger dataset into a `big` folder in the staging volume, but only if it does not exist yet (so re-runs are quick). 500,000 rows is still small for Spark, but enough to show differences in files read.

# COMMAND ----------

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..", "..", "src")))
from shield_data.generate import generate

BIG = Path("/Volumes/shield/landing/staging/big")
if not (BIG / "incident_reports").exists():
    generate(BIG, incidents=500_000, pings=1000, seed=7, dirty=0.0, batches=50)

# COMMAND ----------

# MAGIC %md
# MAGIC Reads the big incident files into a DataFrame and parses the timestamp. Still lazy: nothing is read until a write or action.

# COMMAND ----------

from pyspark.sql import functions as F

df = spark.read.json(f"{BIG}/incident_reports").withColumn("reported_ts", F.to_timestamp("reported_at"))

# COMMAND ----------

# MAGIC %md ## Baseline: unorganised table

# COMMAND ----------

# MAGIC %md
# MAGIC **Baseline:** write the data as it comes, with no layout strategy. `numFiles` and `sizeInBytes` show how many files the table consists of.

# COMMAND ----------

df.write.mode("overwrite").saveAsTable("shield.ops.incidents_plain")
display(spark.sql("DESCRIBE DETAIL shield.ops.incidents_plain").select("numFiles", "sizeInBytes"))

# COMMAND ----------

# MAGIC %md ## Liquid clustering on the columns you filter by

# COMMAND ----------

# MAGIC %md
# MAGIC **Liquid clustering** (`CLUSTER BY`) physically groups rows with similar values of `location_id` and `reported_ts`, so a query filtering on them can skip most files. `OPTIMIZE` applies the clustering.
# MAGIC **Expect:** `clusteringColumns` shows both columns.

# COMMAND ----------

spark.sql("CREATE OR REPLACE TABLE shield.ops.incidents_clustered CLUSTER BY (location_id, reported_ts) AS SELECT * FROM shield.ops.incidents_plain")
spark.sql("OPTIMIZE shield.ops.incidents_clustered")
display(spark.sql("DESCRIBE DETAIL shield.ops.incidents_clustered").select("numFiles", "sizeInBytes", "clusteringColumns"))

# COMMAND ----------

# MAGIC %md ## Same query, two layouts

# COMMAND ----------

# MAGIC %md
# MAGIC The same query on both tables, timed. Notebook timings are **noisy**, so do not trust them alone. The real evidence is in the profile: open **query history**, pick each query, click **See query profile**,
# MAGIC and compare **files read vs. files pruned** and **bytes read**.

# COMMAND ----------

QUERY = """
SELECT COUNT(*) AS n, SUM(casualties) AS casualties
FROM {t}
WHERE location_id = 'L003' AND reported_ts >= '2025-03-01' AND reported_ts < '2025-04-01'
"""
for t in ["shield.ops.incidents_plain", "shield.ops.incidents_clustered"]:
    start = time.time()
    spark.sql(QUERY.format(t=t)).collect()
    print(f"{t}: {time.time() - start:.2f}s")

# COMMAND ----------

# MAGIC %md
# MAGIC Timing in a notebook is noisy. Open both queries in **Query Profile** and compare **files read / files pruned**
# MAGIC and **bytes read**. That is the real evidence that data skipping works.

# COMMAND ----------

# MAGIC %md ## Other habits worth having
# MAGIC * Select only the columns you need; filter early.
# MAGIC * Avoid `collect()` / `toPandas()` on big tables.
# MAGIC * Keep joins on the same type and key; broadcast small dimensions (`F.broadcast`).
# MAGIC * Predictive optimization can run OPTIMIZE/VACUUM for managed tables (check it is enabled for your account).
# MAGIC * Prefer serverless or right-sized job compute; auto-terminate interactive clusters.

# COMMAND ----------

# MAGIC %md
# MAGIC **Broadcast join:** the small `locations` table is copied to every machine so the big table need not be shuffled. `explain()` prints the plan; look for `BroadcastHashJoin`.

# COMMAND ----------

small = spark.table("shield.silver.locations")
joined = spark.table("shield.ops.incidents_plain").join(F.broadcast(small), "location_id")
joined.explain()  # look for BroadcastHashJoin

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Query by `incident_type` only. Is the clustered table still faster? Why or why not?
# MAGIC 2. `ALTER TABLE ... CLUSTER BY (incident_type)` and re-OPTIMIZE. What is the cost of changing keys?
# MAGIC 3. Drop the ops tables when finished: `DROP TABLE shield.ops.incidents_plain`.
