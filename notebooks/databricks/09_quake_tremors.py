# Databricks notebook source
# MAGIC %md
# MAGIC # 09 · Quake tremors
# MAGIC *Daisy Johnson feels the tremors as they happen.*
# MAGIC
# MAGIC **Part A** streams the sensor pings from files (no extra infrastructure).
# MAGIC **Part B** reads the same shape of data from **Event Hubs** through its Kafka endpoint and adds a watermark.
# MAGIC Part B needs a secret and is the least verified part of this repo: see `docs/09-quake-tremors.md`.
# MAGIC
# MAGIC **How to run:** connect compute and run Part A (cells 1 and 2). Part B is optional and needs setup; with the `eventhub_namespace` box empty it prints `Skipping part B` and does nothing.
# MAGIC
# MAGIC **Needs:** chapter 02 done (`sensor_pings` files in the staging volume).
# MAGIC
# MAGIC **What happens:** sensor pings are aggregated into **one-minute windows per location** with Structured Streaming. Part A reads files. Part B reads the same kind of data from Azure Event Hubs
# MAGIC (through its Kafka-compatible endpoint) and adds a **watermark**.

# COMMAND ----------

# MAGIC %md
# MAGIC Two paths: where the ping files are, and where the stream stores its checkpoint (its bookmark so it can restart without losing or double-counting data).

# COMMAND ----------

from pyspark.sql import functions as F

STAGING = "/Volumes/shield/landing/staging/sensor_pings"
CP = "/Volumes/shield/landing/checkpoints/pings"

# COMMAND ----------

# MAGIC %md ## Part A: windowed aggregates over a file stream

# COMMAND ----------

# MAGIC %md
# MAGIC **Structured Streaming** treats incoming data like an ever-growing table; you write normal DataFrame code. Here the source is Auto Loader (`cloudFiles`) over the ping files.
# MAGIC `filter("energy_reading BETWEEN 0 AND 500")` removes sensor glitches (the generator injects `-999` and `1000000`). `F.window("event_time", "1 minute")` buckets events by
# MAGIC **when they happened**, not when they arrived. The query is written with `trigger(availableNow=True)`: process what exists, then stop.
# MAGIC **Expect:** a table of windows (`start`, `end`, `location_id`, `avg_energy`, `pings`).

# COMMAND ----------

pings = (
    spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", f"{CP}/schema")
    .option("cloudFiles.inferColumnTypes", "true")
    .load(STAGING)
    .withColumn("event_time", F.to_timestamp("event_time"))
    .filter("energy_reading BETWEEN 0 AND 500")  # drop sensor glitches (-999, 1e6)
)

per_minute = pings.groupBy(F.window("event_time", "1 minute"), "location_id").agg(
    F.avg("energy_reading").alias("avg_energy"), F.count("*").alias("pings")
)

(
    per_minute.select("window.start", "window.end", "location_id", "avg_energy", "pings")
    .writeStream.outputMode("complete")
    .option("checkpointLocation", f"{CP}/checkpoint_a")
    .trigger(availableNow=True)
    .toTable("shield.silver.ping_windows")
)
display(spark.table("shield.silver.ping_windows").orderBy("start").limit(10))

# COMMAND ----------

# MAGIC %md ## Part B: Event Hubs through the Kafka endpoint
# MAGIC Prerequisites (details in the chapter doc):
# MAGIC 1. A secret scope `shield` with key `eventhubs-conn` holding the namespace connection string.
# MAGIC 2. Pings published with `scripts/send_pings.py`.
# MAGIC 3. Run on **classic job/all-purpose compute** if the Kafka source is not available on your serverless compute.

# COMMAND ----------

# MAGIC %md
# MAGIC Optional Part B. Fill the `eventhub_namespace` box only after you completed *Setting up Part B* in the chapter doc (publish pings with `scripts/send_pings.py`, create the secret scope `shield` with the key `eventhubs-conn`).
# MAGIC The box appears after this cell has run; fill it and run the next cell.

# COMMAND ----------

dbutils.widgets.text("eventhub_namespace", "", "Event Hubs namespace (azd EVENT_HUB_NAMESPACE)")

# COMMAND ----------

# MAGIC %md
# MAGIC Fill the `eventhub_namespace` box (or leave it empty to skip Part B), then run the cell below to read it.

# COMMAND ----------

ns = dbutils.widgets.get("eventhub_namespace")

# COMMAND ----------

# MAGIC %md
# MAGIC Reads Event Hubs via the `kafka` source. The connection string comes from the Databricks secret (never type it into a notebook). `withWatermark("event_time", "10 minutes")` says "wait up to 10 minutes for late events",
# MAGIC which lets Spark finish windows and drop old state. With `append` output a window is written only once the watermark passes its end, so the latest windows may stay missing: correct behaviour.
# MAGIC If the Kafka source is rejected on serverless, switch to classic compute.

# COMMAND ----------

if ns:
    conn = dbutils.secrets.get("shield", "eventhubs-conn")
    jaas = (
        "kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required "
        f'username="$ConnectionString" password="{conn}";'
    )
    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", f"{ns}.servicebus.windows.net:9093")
        .option("subscribe", "sensor-pings")
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.mechanism", "PLAIN")
        .option("kafka.sasl.jaas.config", jaas)
        .option("startingOffsets", "earliest")
        .load()
    )
    schema = "ping_id string, sensor_id string, location_id string, event_time string, energy_reading double"
    live = (
        raw.select(F.from_json(F.col("value").cast("string"), schema).alias("p"))
        .select("p.*")
        .withColumn("event_time", F.to_timestamp("event_time"))
        .withWatermark("event_time", "10 minutes")  # accept events up to 10 minutes late
        .groupBy(F.window("event_time", "1 minute"), "location_id")
        .agg(F.avg("energy_reading").alias("avg_energy"), F.count("*").alias("pings"))
    )
    (
        live.select("window.start", "window.end", "location_id", "avg_energy", "pings")
        .writeStream.outputMode("append")  # a window is emitted once the watermark passes its end
        .option("checkpointLocation", f"{CP}/checkpoint_b")
        .trigger(availableNow=True)
        .toTable("shield.silver.ping_windows_live")
    )
else:
    print("Skipping part B: set the eventhub_namespace widget.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Add an alert table: windows where `avg_energy` is more than 3 standard deviations above the location mean.
# MAGIC 2. Change the watermark to `1 minute`, publish old events, and watch them get dropped.
# MAGIC 3. Why does `append` mode need a watermark and `complete` mode does not? Explain it in two sentences.
