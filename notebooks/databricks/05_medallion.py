# Databricks notebook source
# MAGIC %md
# MAGIC # 05 · Medallion
# MAGIC *Three vaults: raw as received (bronze), cleaned (silver), briefings for the Avengers (gold).*
# MAGIC
# MAGIC Build silver and gold from the bronze tables of chapter 03. This is a simple full-refresh version;
# MAGIC chapters 06 and 08 make it safer and incremental.
# MAGIC
# MAGIC **How to run:** connect serverless compute, then **Run all**.
# MAGIC
# MAGIC **Needs:** chapter 03 done (`shield.bronze.incident_reports` and `shield.bronze.locations`).
# MAGIC
# MAGIC **What happens:** bronze becomes **silver** (one clean row per incident) and then **gold** (aggregates answering business questions).
# MAGIC This version has no quality gate yet, so bad values leak into gold: you will see that at the end. Safe to re-run: all writes are full overwrites.

# COMMAND ----------

from pyspark.sql import Window
from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %md ## Silver: typed, deduplicated incidents (no quality gate yet)

# COMMAND ----------

# MAGIC %md
# MAGIC Two steps. 1) `try_to_timestamp` converts the text `reported_at` into a real timestamp, giving NULL instead of an error for garbage.
# MAGIC 2) A **window function** numbers the rows of each `incident_id` from newest to oldest by `_ingested_at`; we keep row 1 only. That removes duplicates (the latest copy wins).
# MAGIC The result is written to `shield.silver.incident_reports`. **Expect:** a count lower than the bronze row count.

# COMMAND ----------

bronze = spark.table("shield.bronze.incident_reports")

latest = Window.partitionBy("incident_id").orderBy(F.col("_ingested_at").desc())
silver = (
    bronze.withColumn("reported_ts", F.expr("try_to_timestamp(reported_at, \"yyyy-MM-dd'T'HH:mm:ss'Z'\")"))
    .withColumn("rn", F.row_number().over(latest))
    .filter("rn = 1")
    .drop("rn")
)
silver.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("shield.silver.incident_reports")
print(spark.table("shield.silver.incident_reports").count())

# COMMAND ----------

# MAGIC %md ## Silver: locations

# COMMAND ----------

# MAGIC %md
# MAGIC Locations need no cleaning here, so we just select the columns we want and save them as a silver table.

# COMMAND ----------

(
    spark.table("shield.bronze.locations")
    .select("location_id", "city", "country", "lat", "lon")
    .write.mode("overwrite").saveAsTable("shield.silver.locations")
)

# COMMAND ----------

# MAGIC %md ## Gold: business-ready aggregates

# COMMAND ----------

# MAGIC %md
# MAGIC **Gold table 1:** incidents and casualties per day, city, type and severity. It joins incidents with locations (`USING (location_id)`) and groups by all non-aggregated columns (`GROUP BY ALL`).
# MAGIC Named after the question it answers: "what is the daily threat picture?". **Expect:** 10 recent rows.

# COMMAND ----------

spark.sql(
    """
    CREATE OR REPLACE TABLE shield.gold.daily_threat_briefing AS
    SELECT
      CAST(i.reported_ts AS DATE) AS report_date,
      l.city,
      l.country,
      i.incident_type,
      i.severity,
      COUNT(*)            AS incidents,
      SUM(i.casualties)   AS casualties
    FROM shield.silver.incident_reports i
    JOIN shield.silver.locations l USING (location_id)
    WHERE i.reported_ts IS NOT NULL
    GROUP BY ALL
    """
)
display(spark.sql("SELECT * FROM shield.gold.daily_threat_briefing ORDER BY report_date DESC LIMIT 10"))

# COMMAND ----------

# MAGIC %md ## Gold: location risk ranking

# COMMAND ----------

# MAGIC %md
# MAGIC **Gold table 2:** per city, how many incidents, how many were `high` or `critical`, and the average casualties. **Expect:** cities ranked by serious incidents.

# COMMAND ----------

spark.sql(
    """
    CREATE OR REPLACE TABLE shield.gold.location_risk AS
    SELECT
      l.city,
      COUNT(*) AS incidents,
      SUM(CASE WHEN i.severity IN ('high','critical') THEN 1 ELSE 0 END) AS serious_incidents,
      ROUND(AVG(i.casualties), 2) AS avg_casualties
    FROM shield.silver.incident_reports i
    JOIN shield.silver.locations l USING (location_id)
    GROUP BY l.city
    """
)
display(spark.table("shield.gold.location_risk").orderBy(F.desc("serious_incidents")))

# COMMAND ----------

# MAGIC %md
# MAGIC Notice what is **wrong** with this silver table: invalid severities, future timestamps and negative casualties
# MAGIC flowed straight through, and they are now in the gold numbers. That is chapter 06.

# COMMAND ----------

# MAGIC %md
# MAGIC **Look closely.** Valid severities are `low`, `medium`, `high`, `critical`. Anything else (like `catastrophic`) got through to silver and into the gold numbers. Chapter 06 adds the gate that stops this.

# COMMAND ----------

display(spark.sql("SELECT severity, COUNT(*) FROM shield.silver.incident_reports GROUP BY severity"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Add `gold.agent_workload`: incidents per agent codename (join `silver.agents`).
# MAGIC 2. Which of the silver transformations is not idempotent if you run the notebook twice? (Hint: it is, why?)
# MAGIC 3. Sketch what each layer would hold for a retail dataset you know.
