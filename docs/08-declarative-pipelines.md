# 08 · Declarative pipelines

**Code:** [pipelines/shield_insight.py](../pipelines/shield_insight.py) · **Notebook:** [08_declarative_pipelines.py](../notebooks/databricks/08_declarative_pipelines.py)

## Concepts
Lakeflow Spark Declarative Pipelines (formerly Delta Live Tables) let you declare datasets; the engine builds the dependency graph, handles checkpoints, retries, and incremental processing.

| Decorator | Creates | Use for |
|---|---|---|
| `@dp.table` returning a **streaming** DataFrame | Streaming table | Append-style ingestion and incremental transforms |
| `@dp.materialized_view` returning a **batch** DataFrame | Materialized view | Aggregates and joins, refreshed incrementally when possible |
| `@dp.expect` / `expect_or_drop` / `expect_or_fail` | Quality rule | Warn / drop / fail on violating rows; metrics go to the event log |

Import with `from pyspark import pipelines as dp` (older material uses `import dlt`).

## Compared with chapters 03–06
Same bronze → silver → gold, but you wrote **no** checkpoint paths, no write logic, and no orchestration between tables. The trade-off: less control, more convention. The rules here mirror `quality.py`.

## Gotchas
* Pipeline code is evaluated to *build a graph*; avoid side effects (no writes, no `display`) in dataset functions.
* `dropDuplicates` on a stream keeps unbounded state; production code bounds it with a watermark.
* Reading a dataset by bare name (`incidents_bronze`) resolves within the pipeline's catalog/schema.
* Run on serverless to avoid cluster setup.

## Try it yourself
See the notebook. Bonus: compare the cost (DBUs) of the pipeline run vs the notebook version, using the system tables from chapter 16.
