"""Lakeflow Spark Declarative Pipeline: raw incident files -> bronze -> silver -> gold.

Run it as a pipeline (chapter 08) or deploy it with the bundle (chapter 13). It is NOT a notebook:
the decorators only work inside a pipeline. Target catalog and schema come from the pipeline settings.
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F

RAW = spark.conf.get("raw_path", "/Volumes/shield/landing/raw")
TS_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'"


@dp.table(comment="Raw incident reports, ingested incrementally with Auto Loader")
def incidents_bronze():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(f"{RAW}/incident_reports")
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_ingested_at", F.current_timestamp())
    )


@dp.table(comment="Typed incidents that passed the quality rules")
@dp.expect_or_drop("has_agent", "agent_id IS NOT NULL")
@dp.expect_or_drop("valid_timestamp", "reported_ts IS NOT NULL AND reported_ts <= current_timestamp()")
@dp.expect_or_drop("valid_severity", "severity IN ('low', 'medium', 'high', 'critical')")
@dp.expect_or_drop("non_negative_casualties", "casualties IS NOT NULL AND casualties >= 0")
def incidents_silver():
    return (
        spark.readStream.table("incidents_bronze")
        .withColumn("reported_ts", F.expr(f"try_to_timestamp(reported_at, \"{TS_FORMAT}\")"))
        .dropDuplicates(["incident_id"])  # unbounded state: fine for learning, add a watermark in production
    )


@dp.materialized_view(comment="Daily incident counts per type and severity")
def daily_threat_briefing():
    return (
        spark.read.table("incidents_silver")
        .groupBy(F.to_date("reported_ts").alias("report_date"), "incident_type", "severity")
        .agg(F.count("*").alias("incidents"), F.sum("casualties").alias("casualties"))
    )
