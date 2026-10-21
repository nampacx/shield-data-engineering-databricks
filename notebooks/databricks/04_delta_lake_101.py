# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Delta Lake 101
# MAGIC *Every write is all-or-nothing, so a half-written report never reaches an analyst.*
# MAGIC
# MAGIC Needs chapter 03 (`shield.bronze.agents`). You will: enforce a schema, evolve it, upsert with `MERGE`,
# MAGIC and maintain the table with `OPTIMIZE` / `VACUUM`.
# MAGIC
# MAGIC **How to run:** connect serverless compute, then **Run all** (or step through).
# MAGIC
# MAGIC **Needs:** chapter 03 done (`shield.bronze.agents`).
# MAGIC
# MAGIC **What happens:** you create a small Delta table and test what Delta guarantees: bad writes are rejected, schema changes are explicit, `MERGE` upserts,
# MAGIC every change is logged, and small files can be compacted. Safe to re-run: the first cell resets the table with `CREATE OR REPLACE`.

# COMMAND ----------

# MAGIC %md
# MAGIC Copies the agents from bronze into a Delta table in silver, keeping five columns. `DESCRIBE DETAIL` shows table facts: format (`delta`), location, number of files, size.

# COMMAND ----------

from pyspark.sql import functions as F

spark.sql("CREATE OR REPLACE TABLE shield.silver.agents AS "
          "SELECT agent_id, codename, clearance_level, home_location_id, active FROM shield.bronze.agents")
display(spark.sql("DESCRIBE DETAIL shield.silver.agents"))

# COMMAND ----------

# MAGIC %md ## Schema enforcement: bad writes are rejected

# COMMAND ----------

# MAGIC %md
# MAGIC We try to append a row that has fewer columns and a wrong type than the table. Delta checks every write against the table schema and refuses.
# MAGIC **Expect:** `Rejected: ...` (an exception name) and no new row.

# COMMAND ----------

bad = spark.createDataFrame([("A9999", "Ghost", "top-secret")], "agent_id string, codename string, clearance_level string")
try:
    bad.write.mode("append").saveAsTable("shield.silver.agents")
except Exception as e:  # noqa: BLE001
    print("Rejected:", type(e).__name__)

# COMMAND ----------

# MAGIC %md ## Schema evolution is explicit

# COMMAND ----------

# MAGIC %md
# MAGIC Changing the schema is allowed, but explicit: you must say so. This adds a nullable `last_seen` column. **Expect:** the column list now ends with `last_seen`.

# COMMAND ----------

spark.sql("ALTER TABLE shield.silver.agents ADD COLUMNS (last_seen DATE)")
spark.sql("DESCRIBE shield.silver.agents").show()

# COMMAND ----------

# MAGIC %md ## MERGE: upsert a field update (promotions + new recruits)

# COMMAND ----------

# MAGIC %md
# MAGIC **MERGE** = upsert in one atomic statement. The updates contain one existing agent (`A0001`, promoted: matched, so UPDATE) and one new recruit (`A9001`: not matched, so INSERT).
# MAGIC The updates must have one row per `agent_id`, otherwise MERGE fails. **Expect:** two rows, `A0001` updated and `A9001` new.

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

# MAGIC %md
# MAGIC Delta's transaction log as a table: one row per version with the operation (`CREATE OR REPLACE`, `ADD COLUMNS`, `MERGE`...), the user and metrics. This is the base for time travel in chapter 07.

# COMMAND ----------

display(spark.sql("DESCRIBE HISTORY shield.silver.agents"))

# COMMAND ----------

# MAGIC %md ## Many small writes → many small files → slow reads

# COMMAND ----------

# MAGIC %md
# MAGIC The *small files problem*: 15 separate inserts create 15 small files. **Expect:** `numFiles` = 15 in the output.

# COMMAND ----------

spark.sql("CREATE OR REPLACE TABLE shield.silver.small_files_demo (id BIGINT, v STRING)")
for i in range(15):
    spark.sql(f"INSERT INTO shield.silver.small_files_demo VALUES ({i}, 'x')")
display(spark.sql("DESCRIBE DETAIL shield.silver.small_files_demo").select("numFiles", "sizeInBytes"))

# COMMAND ----------

# MAGIC %md
# MAGIC `OPTIMIZE` compacts many small files into fewer big ones. **Expect:** `numFiles` drops to 1. The data is identical; reads are faster.

# COMMAND ----------

spark.sql("OPTIMIZE shield.silver.small_files_demo")
display(spark.sql("DESCRIBE DETAIL shield.silver.small_files_demo").select("numFiles", "sizeInBytes"))

# COMMAND ----------

# MAGIC %md
# MAGIC `VACUUM` deletes files no longer referenced by the table (default retention 7 days). It also ends how far back
# MAGIC time travel can go (chapter 07). Do not shorten the retention on tables you care about.

# COMMAND ----------

# MAGIC %md
# MAGIC `DRY RUN` lists the files `VACUUM` *would* delete without deleting anything. **Expect:** possibly an empty list, because files younger than 7 days are kept.

# COMMAND ----------

display(spark.sql("VACUUM shield.silver.small_files_demo DRY RUN"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Make the MERGE idempotent-safe: what happens if the `USING` side has two rows for the same `agent_id`?
# MAGIC 2. Add `WHEN NOT MATCHED BY SOURCE` to deactivate agents missing from the update.
# MAGIC 3. Compare `numFiles` before/after OPTIMIZE on `bronze.incident_reports`.
