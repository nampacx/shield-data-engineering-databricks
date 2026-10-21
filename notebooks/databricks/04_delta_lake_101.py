# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Delta Lake 101
# MAGIC *Every write is all-or-nothing, so a half-written report never reaches an analyst.*
# MAGIC
# MAGIC Needs chapter 03 (`shield.bronze.agents`). You will: enforce a schema, evolve it, upsert with `MERGE`,
# MAGIC and maintain the table with `OPTIMIZE` / `VACUUM`.

# COMMAND ----------

from pyspark.sql import functions as F

spark.sql("CREATE OR REPLACE TABLE shield.silver.agents AS "
          "SELECT agent_id, codename, clearance_level, home_location_id, active FROM shield.bronze.agents")
display(spark.sql("DESCRIBE DETAIL shield.silver.agents"))

# COMMAND ----------

# MAGIC %md ## Schema enforcement: bad writes are rejected

# COMMAND ----------

bad = spark.createDataFrame([("A9999", "Ghost", "top-secret")], "agent_id string, codename string, clearance_level string")
try:
    bad.write.mode("append").saveAsTable("shield.silver.agents")
except Exception as e:  # noqa: BLE001
    print("Rejected:", type(e).__name__)

# COMMAND ----------

# MAGIC %md ## Schema evolution is explicit

# COMMAND ----------

spark.sql("ALTER TABLE shield.silver.agents ADD COLUMNS (last_seen DATE)")
spark.sql("DESCRIBE shield.silver.agents").show()

# COMMAND ----------

# MAGIC %md ## MERGE: upsert a field update (promotions + new recruits)

# COMMAND ----------

updates = spark.createDataFrame(
    [("A0001", "Falcon-01", 5, "L001", True), ("A9001", "Newbie-01", 1, "L002", True)],
    "agent_id string, codename string, clearance_level int, home_location_id string, active boolean",
).withColumn("last_seen", F.current_date())
updates.createOrReplaceTempView("agent_updates")

spark.sql(
    """
    MERGE INTO shield.silver.agents AS t
    USING agent_updates AS s
    ON t.agent_id = s.agent_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
    """
)
display(spark.sql("SELECT * FROM shield.silver.agents WHERE agent_id IN ('A0001','A9001')"))

# COMMAND ----------

# MAGIC %md ## The transaction log

# COMMAND ----------

display(spark.sql("DESCRIBE HISTORY shield.silver.agents"))

# COMMAND ----------

# MAGIC %md ## Many small writes → many small files → slow reads

# COMMAND ----------

spark.sql("CREATE OR REPLACE TABLE shield.silver.small_files_demo (id BIGINT, v STRING)")
for i in range(15):
    spark.sql(f"INSERT INTO shield.silver.small_files_demo VALUES ({i}, 'x')")
display(spark.sql("DESCRIBE DETAIL shield.silver.small_files_demo").select("numFiles", "sizeInBytes"))

# COMMAND ----------

spark.sql("OPTIMIZE shield.silver.small_files_demo")
display(spark.sql("DESCRIBE DETAIL shield.silver.small_files_demo").select("numFiles", "sizeInBytes"))

# COMMAND ----------

# MAGIC %md
# MAGIC `VACUUM` deletes files no longer referenced by the table (default retention 7 days). It also ends how far back
# MAGIC time travel can go (chapter 07). Do not shorten the retention on tables you care about.

# COMMAND ----------

display(spark.sql("VACUUM shield.silver.small_files_demo DRY RUN"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Make the MERGE idempotent-safe: what happens if the `USING` side has two rows for the same `agent_id`?
# MAGIC 2. Add `WHEN NOT MATCHED BY SOURCE` to deactivate agents missing from the update.
# MAGIC 3. Compare `numFiles` before/after OPTIMIZE on `bronze.incident_reports`.
