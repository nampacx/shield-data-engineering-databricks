# Databricks notebook source
# MAGIC %md
# MAGIC # 06 · Natasha spots the fake
# MAGIC *A forged ping has a timestamp from the future. Quality rules turn her instinct into code.*
# MAGIC
# MAGIC Pattern: evaluate named rules on every row → valid rows to silver, invalid rows to a **quarantine** table
# MAGIC with the list of rules they failed. Nothing is silently dropped.

# COMMAND ----------

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..", "..", "src")))
from pyspark.sql import Window
from pyspark.sql import functions as F

from shield_data.quality import INCIDENT_RULES

INCIDENT_RULES

# COMMAND ----------

# MAGIC %md ## Evaluate every rule per row

# COMMAND ----------

bronze = spark.table("shield.bronze.incident_reports")
parsed = bronze.withColumn("reported_ts", F.expr("try_to_timestamp(reported_at, \"yyyy-MM-dd'T'HH:mm:ss'Z'\")"))

# One array column listing the rules this row FAILED. coalesce: a NULL result counts as a failure.
failed = F.array(
    *[F.when(F.coalesce(F.expr(expr), F.lit(False)), F.lit(None)).otherwise(F.lit(name)) for name, expr in INCIDENT_RULES.items()]
)
checked = parsed.withColumn("failed_rules", F.filter(failed, lambda x: x.isNotNull()))

# COMMAND ----------

valid = checked.filter(F.size("failed_rules") == 0).drop("failed_rules")
invalid = checked.filter(F.size("failed_rules") > 0)
print("valid:", valid.count(), "invalid:", invalid.count())

# COMMAND ----------

# MAGIC %md ## Silver (deduplicated, valid only) and quarantine

# COMMAND ----------

latest = Window.partitionBy("incident_id").orderBy(F.col("_ingested_at").desc())
(
    valid.withColumn("rn", F.row_number().over(latest)).filter("rn = 1").drop("rn")
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("shield.silver.incident_reports")
)
(
    invalid.withColumn("_quarantined_at", F.current_timestamp())
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("shield.silver.incident_reports_quarantine")
)

# COMMAND ----------

# MAGIC %md ## Which rules fail most?

# COMMAND ----------

display(
    spark.table("shield.silver.incident_reports_quarantine")
    .select(F.explode("failed_rules").alias("rule"))
    .groupBy("rule").count().orderBy(F.desc("count"))
)

# COMMAND ----------

# MAGIC %md ## Rebuild gold on clean data
# MAGIC Re-run the gold cells of notebook 05 (or this one-liner) and compare the numbers.

# COMMAND ----------

display(spark.sql("SELECT severity, COUNT(*) AS n FROM shield.silver.incident_reports GROUP BY severity"))

# COMMAND ----------

# MAGIC %md ## Belt and braces: a Delta CHECK constraint
# MAGIC Rules in the pipeline catch bad data on the way in; a constraint makes the table itself refuse it.

# COMMAND ----------

spark.sql("ALTER TABLE shield.silver.incident_reports ADD CONSTRAINT non_negative_casualties CHECK (casualties >= 0)")
try:
    spark.sql("INSERT INTO shield.silver.incident_reports (incident_id, casualties) VALUES ('BAD', -1)")
except Exception as e:  # noqa: BLE001
    print("Rejected by constraint:", type(e).__name__)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Add a rule: `agent_id` must exist in `silver.agents`. Which rows fail now?
# MAGIC 2. Turn the quarantine counts into a daily quality table in `shield.ops` (rule, date, failed_rows).
# MAGIC 3. Decide: for which rule would you rather *fail the job* than quarantine? Why?
