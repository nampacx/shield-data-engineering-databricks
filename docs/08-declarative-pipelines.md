# 08 · Declarative pipelines

**Code:** [pipelines/shield_insight.py](../pipelines/shield_insight.py) · **Notebook:** [08_declarative_pipelines.py](../notebooks/databricks/08_declarative_pipelines.py)

## How to run this chapter

**Before you start:** chapters 03 and 05 are done and raw files have been delivered to `shield.landing.raw` (notebook 03 does that). This chapter is the exception: **the pipeline is created in the UI**, and the notebook only inspects the results.

**Steps**
1. Open the notebook and connect serverless compute ([How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3). Run only the first code cell, which creates the schema `shield.pipeline`.
2. In the left sidebar choose **Jobs & Pipelines → Create → ETL pipeline** and fill in the settings listed at the top of the notebook (name `shield_insight`, catalog `shield`, schema `pipeline`, source file `pipelines/shield_insight.py` from your Git folder, serverless compute, configuration `raw_path = /Volumes/shield/landing/raw`).
3. Click **Run pipeline** and wait until the graph shows every table as completed.
4. Back in the notebook, run the remaining cells to query the tables the pipeline created.
5. Optional: deliver more files (`deliver()` from notebook 03), run the pipeline again, and see that only the new files are processed.

**What you should see:** the pipeline's tables (for example `incidents_silver` and `daily_threat_briefing`) in `shield.pipeline`, plus data-quality numbers on the `incidents_silver` node.

Do **not** run `pipelines/shield_insight.py` as a normal notebook: the `@dp` decorators only work inside a pipeline. The event-log cell may need its table name adjusted for your pipeline; the notebook explains where to find it.

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
