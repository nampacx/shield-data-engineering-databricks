# 09 · Quake tremors

**Notebook:** [09_quake_tremors.ipynb](../notebooks/databricks/09_quake_tremors.ipynb) · **Producer:** [scripts/send_pings.py](../scripts/send_pings.py)

> Status: **Part A** is plain Structured Streaming over files. **Part B (Event Hubs) is the least verified piece of the repo**: it needs a secret and compute that supports the Kafka source, and it was never run against a real namespace. The numbers in the notebook are expectations until someone has run it in a workspace.

## Concepts
* **Structured Streaming** treats a stream as an ever-growing table; your query is the same DataFrame code.
* **Event time vs processing time**: aggregate by *when it happened*, not when it arrived.
* **Windows**: `F.window("event_time", "1 minute")` buckets events.
* **Watermark**: "I will wait this long for late events." It bounds state and tells the engine when a window is final. `append` output needs a watermark (a window is written once final, so every row is delayed by at least the watermark); `complete` keeps all state forever and does not need one.
* **Checkpoints** make streams restartable with exactly-once results to Delta.
* **`availableNow` trigger**: process what is there, then stop. It is the cheap way to run a stream on a schedule (chapter 10) and the one Learn recommends on serverless compute.
* **Event Hubs** exposes a Kafka-compatible endpoint (`<namespace>.servicebus.windows.net:9093`), so Spark's `kafka` source works.

## What the notebook does
Part A (Steps 1 to 3): count the sensor glitches in the raw files (966 of 20,000 pings), run the one-minute window aggregation once (11,622 window rows over 19,034 usable pings), then run it again and see that nothing changes because of the checkpoint.
Part B (Step 4): the same aggregation from Event Hubs with a 10-minute watermark and `append` output. The clean-up section drops the tables and the checkpoint folder. The numbers assume the chapter 02 dataset.

## Setting up Part B
1. `pip install azure-eventhub azure-identity` and run `python scripts/send_pings.py --namespace <EVENT_HUB_NAMESPACE> --count 500` (you have *Event Hubs Data Owner* from Bicep).
2. Get a connection string: Azure portal → Event Hubs namespace → *Shared access policies*. For learning, `RootManageSharedAccessKey` works, but it can send and manage too. Better: create a policy with **Listen** only (the notebook only reads). Use Microsoft Entra authentication in production.
3. Create a Databricks secret scope and key. Easiest with the CLI: `databricks secrets create-scope shield` then `databricks secrets put-secret shield eventhubs-conn`. (A Key Vault-backed scope is the production option.)
4. Fill the `eventhub_namespace` widget and run Step 4. Learn recommends the `availableNow` trigger for Kafka on serverless; if the Kafka source is rejected on your compute, use classic compute.

## Gotchas
* In `availableNow` mode with `append`, windows that are not yet final stay unwritten: that is correct behaviour, not a bug. `send_pings.py` stamps pings with the time they are sent, so one burst of 500 pings gives **no rows** until a later ping moves the watermark more than 10 minutes past them. Publish again after 11 minutes and re-run Step 4.
* `kafkashaded.` in the JAAS class name is required on Databricks.
* Filter sensor glitches before aggregating (the generator injects `-999` and `1e6`).
* Never put the connection string in a cell, a widget or a commit.
* The namespace costs money while it exists. Remove the secret (`databricks secrets delete-secret shield eventhubs-conn`) and run `azd down --purge` when you are finished.

## Try it yourself
1. Add an alert table: windows where `avg_energy` is more than 3 standard deviations above the mean of the same location. Which location alerts most often, and are the alerts real or a few lonely pings in a window?
2. Make the checkpoint do work: copy one more JSON file into `/Volumes/shield/landing/staging/sensor_pings` (any copy with a new name; delete it afterwards) and re-run Step 2. How many rows are added or changed, and why does `complete` mode rewrite the whole table?
3. Estimate the cost of keeping a 24/7 stream running against a 5-minute scheduled `availableNow` job. Then change the Part B watermark to `1 minute`, publish events with an old `event_time`, and watch them get dropped.
