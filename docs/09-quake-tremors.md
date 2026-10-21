# 09 · Quake tremors

**Notebook:** [09_quake_tremors.py](../notebooks/databricks/09_quake_tremors.py) · **Producer:** [scripts/send_pings.py](../scripts/send_pings.py)

> Status: **Part A** is plain Structured Streaming. **Part B (Event Hubs) is the least verified piece of the repo**: it needs a secret and compute that supports the Kafka source.

## Concepts
* **Structured Streaming** treats a stream as an ever-growing table; your query is the same DataFrame code.
* **Event time vs processing time**: aggregate by *when it happened*, not when it arrived.
* **Windows**: `F.window("event_time", "1 minute")` buckets events.
* **Watermark**: "I will wait this long for late events." It bounds state and tells the engine when a window is final. `append` output needs a watermark (a window is emitted once final); `complete`/`update` do not.
* **Checkpoints** make streams restartable with exactly-once results to Delta.
* **Event Hubs** exposes a Kafka-compatible endpoint (`<namespace>.servicebus.windows.net:9093`), so Spark's `kafka` source works.

## Setting up Part B
1. `pip install azure-eventhub azure-identity` and run `python scripts/send_pings.py --namespace <EVENT_HUB_NAMESPACE> --count 500` (you have *Event Hubs Data Owner* from Bicep).
2. Get a connection string: Azure portal → Event Hubs namespace → *Shared access policies* → `RootManageSharedAccessKey` (learning only; use Entra auth in production).
3. Create a Databricks secret scope and key. Easiest with the CLI: `databricks secrets create-scope shield` then `databricks secrets put-secret shield eventhubs-conn`. (A Key Vault-backed scope is the production option.)
4. Run on classic compute if the Kafka source is rejected on serverless. Fill the widget and run Part B.

## Gotchas
* In `availableNow` mode with `append`, the last windows stay open until a later event moves the watermark: that is correct behaviour, not a bug.
* `kafkashaded.` in the JAAS class name is required on Databricks.
* Filter sensor glitches before aggregating (the generator injects `-999` and `1e6`).

## Try it yourself
See the notebook. Bonus: estimate the cost of keeping a 24/7 stream running vs a 5-minute scheduled `availableNow` job.
