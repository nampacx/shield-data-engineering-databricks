# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · Coulson ingests
# MAGIC *Files arrive late, twice, and in new shapes. Auto Loader does not mind.*
# MAGIC
# MAGIC Goal: land raw files into **bronze** Delta tables incrementally, remembering what was already read.
# MAGIC Expect one deliberate failure in the schema-drift section.
# MAGIC
# MAGIC **How to run:** connect serverless compute and run the cells **one by one** (Shift+Enter) the first time, reading the printed counts.
# MAGIC
# MAGIC **Needs:** chapter 02 done (staged files in `shield.landing.staging`).
# MAGIC
# MAGIC **What happens:** two helper functions are defined. `deliver()` copies the next staged file into the `raw` volume (simulating a delivery from the field).
# MAGIC `ingest()` uses **Auto Loader** to load only *new* files from `raw` into a bronze Delta table, remembering what it already read in a checkpoint.
# MAGIC Expected on purpose: one failure in the schema-drift section, caught and printed as `Expected failure: ...`.

# COMMAND ----------

# MAGIC %md
# MAGIC **The two helpers.** `deliver(feed, n)` copies the next `n` files that are not yet in `raw`. `ingest(feed, fmt, table)` reads `raw` with `cloudFiles` (Auto Loader),
# MAGIC stores the inferred schema in `schemaLocation`, adds two lineage columns (`_source_file`, `_ingested_at`), and writes to `shield.bronze.<table>`.
# MAGIC `trigger(availableNow=True)` means "process everything new, then stop": incremental *batch*, not an endless stream. Run this cell; it only defines functions, so nothing is printed.

# COMMAND ----------

import shutil
from pathlib import Path

from pyspark.sql import functions as F

STAGING = Path("/Volumes/shield/landing/staging")
RAW = Path("/Volumes/shield/landing/raw")
CP = "/Volumes/shield/landing/checkpoints"


def deliver(feed: str, n: int = 1) -> None:
    """Move the next `n` staged files of a feed into the raw landing zone (like a field delivery)."""
    (RAW / feed).mkdir(parents=True, exist_ok=True)
    delivered = {p.name for p in (RAW / feed).glob("*")}
    todo = [p for p in sorted((STAGING / feed).glob("*")) if p.name not in delivered][:n]
    for p in todo:
        shutil.copy(p, RAW / feed / p.name)
    print(f"{feed}: delivered {[p.name for p in todo]}")


def ingest(feed: str, fmt: str, table: str) -> None:
    """Incrementally load new files of `feed` into a bronze table with Auto Loader."""
    reader = (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", fmt)
        .option("cloudFiles.schemaLocation", f"{CP}/{feed}/schema")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
    )
    if fmt == "csv":
        reader = reader.option("header", "true")
    (
        reader.load(f"{RAW}/{feed}")
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_ingested_at", F.current_timestamp())
        .writeStream.option("checkpointLocation", f"{CP}/{feed}/checkpoint")
        .option("mergeSchema", "true")
        .trigger(availableNow=True)  # process what is there, then stop
        .toTable(f"shield.bronze.{table}")
    )


# COMMAND ----------

# MAGIC %md ## Dimension feeds (CSV): one delivery each

# COMMAND ----------

# MAGIC %md
# MAGIC The three small CSV feeds (agents, locations, threat assessments) are delivered once and ingested. **Expect:** three `delivered [...]` lines.
# MAGIC Check **Catalog → shield → bronze** afterwards: three new tables.

# COMMAND ----------

for feed in ["agents", "locations", "threat_assessments"]:
    deliver(feed)
    ingest(feed, "csv", feed)

# COMMAND ----------

# MAGIC %md ## Incident reports (JSON): deliveries trickle in

# COMMAND ----------

# MAGIC %md
# MAGIC The first incident file arrives and is loaded. **Expect:** a row count (a bit under 2,000). Remember it.

# COMMAND ----------

deliver("incident_reports", 1)
ingest("incident_reports", "json", "incident_reports")
print(spark.table("shield.bronze.incident_reports").count())

# COMMAND ----------

# MAGIC %md
# MAGIC Same call, no new file. **Expect:** the *same* count. This is the checkpoint at work: Auto Loader knows it already read everything.

# COMMAND ----------

# Running again with no new files processes nothing: that is the checkpoint at work.
ingest("incident_reports", "json", "incident_reports")
print(spark.table("shield.bronze.incident_reports").count())

# COMMAND ----------

# MAGIC %md
# MAGIC Three more files arrive. **Expect:** the count rises by about three files' worth of rows.

# COMMAND ----------

deliver("incident_reports", 3)
ingest("incident_reports", "json", "incident_reports")
print(spark.table("shield.bronze.incident_reports").count())

# COMMAND ----------

# MAGIC %md ## Schema drift
# MAGIC The last file contains a new field, `source_channel`. With `addNewColumns`, the stream **fails once** after
# MAGIC recording the new schema, and the next run succeeds. In production a Lakeflow Job retry does this for you (chapter 10).

# COMMAND ----------

# MAGIC %md
# MAGIC The last file has a new field. With `addNewColumns`, Auto Loader stops once after saving the new schema. We catch the error so the notebook keeps going.
# MAGIC **Expect:** a line starting with `Expected failure:`. That is the lesson, not a problem.

# COMMAND ----------

deliver("incident_reports", 1)
try:
    ingest("incident_reports", "json", "incident_reports")
except Exception as e:  # noqa: BLE001
    print("Expected failure:", type(e).__name__, str(e)[:200])

# COMMAND ----------

# MAGIC %md
# MAGIC Run the ingest again: now it succeeds, and the new column `source_channel` exists. Older rows have `NULL` there. **Expect:** a table with some `source_channel` values.

# COMMAND ----------

ingest("incident_reports", "json", "incident_reports")
display(spark.table("shield.bronze.incident_reports").filter("source_channel IS NOT NULL").limit(5))

# COMMAND ----------

# MAGIC %md ## Bronze keeps everything, including duplicates and bad rows

# COMMAND ----------

# MAGIC %md
# MAGIC Bronze keeps everything, including duplicates and bad rows, on purpose: it is your audit trail and your replay source.
# MAGIC **Expect:** more rows than distinct `incident_id`s. Chapters 05 and 06 clean this up.

# COMMAND ----------

bronze = spark.table("shield.bronze.incident_reports")
print("rows:", bronze.count(), "distinct incident_ids:", bronze.select("incident_id").distinct().count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Re-`deliver` an already delivered file under a new name. What does Auto Loader do?
# MAGIC 2. Switch `schemaEvolutionMode` to `rescue` and look at `_rescued_data` after the drift file.
# MAGIC 3. Ingest `sensor_pings` too, and compare file count vs. row count.
