# 08 · Declarative pipelines

**Code:** [pipelines/shield_insight.py](../pipelines/shield_insight.py) · **Notebook:** [08_declarative_pipelines.ipynb](../notebooks/databricks/08_declarative_pipelines.ipynb)

## Concepts
Lakeflow Spark Declarative Pipelines (formerly Delta Live Tables) let you declare datasets; the engine builds the dependency graph, handles checkpoints, retries, and incremental processing. The product is generally available and needs the Premium plan. Features near it that are in preview or beta (Genie Code in the pipeline editor, the `pipeline_events` system table, standalone pipeline decorators in notebooks) are not used here.

| Decorator | Creates | Use for |
|---|---|---|
| `@dp.table` returning a **streaming** DataFrame | Streaming table | Append-style ingestion and incremental transforms |
| `@dp.materialized_view` returning a **batch** DataFrame | Materialized view | Aggregates and joins, refreshed incrementally when possible |
| `@dp.expect` / `expect_or_drop` / `expect_or_fail` | Quality rule (expectation) | Warn / drop / fail on violating rows; metrics go to the event log |

Import with `from pyspark import pipelines as dp` (older material uses `import dlt`). `@dp.expect` and friends are Databricks additions, not part of open-source Spark.

## What the notebook does
It opens with an explainer (declarative pipelines, streaming table vs materialized view, expectations, event log), then six steps, each with a goal, an expected result and a check table:

1. Create the pipeline in the UI (**New → ETL pipeline**, default catalog `shield`, schema `pipeline`, source file `pipelines/shield_insight.py`) and **Dry run** it. UI step, no code.
2. **Run pipeline**. The three datasets appear in `shield.pipeline`; `incidents_bronze` holds 10,250 rows.
3. Silver has 9,500 unique incidents and none that fails a rule from `INCIDENT_RULES`.
4. The `daily_threat_briefing` materialized view has 4,975 rows covering all 9,500 incidents.
5. The event log shows how many rows each expectation rejected (95, 205, 109, 91 expected).
6. Run again with no new files: nothing is reprocessed. UI step plus a check.

It is standalone: it reads the raw files from chapter 03's landing zone through the pipeline's own checkpoint, so it needs neither the bronze nor the silver tables of chapters 03 to 06. Nothing has been run in a workspace yet, so the expected values are expectations, and the UI labels come from Microsoft Learn.

## Compared with chapters 03–06
Same bronze → silver → gold idea, but you wrote **no** checkpoint paths, no write logic, and no orchestration between tables. The trade-off: less control, more convention. The rules mirror `quality.py` (the pipeline file repeats the four conditions, and Step 5 checks that the expectation names match `INCIDENT_RULES`). Differences to keep in mind:

* The pipeline writes to `shield.pipeline` and never touches `shield.bronze`, `shield.silver` or `shield.gold`.
* Rejected rows are dropped and only counted in the event log. There is no quarantine table.
* `dropDuplicates` keeps the first copy of an incident; chapters 05 and 06 keep the latest. The copies are identical in this dataset, so the result is the same.
* The gold view groups by date, type and severity only. It has no `city`, because the pipeline does not read the locations feed, so it is not the same table as `shield.gold.daily_threat_briefing`.
* The bundle in chapter 13 deploys this file as `shield_insight_<target>` into schema `pipeline_<target>`, not `pipeline`.

## Gotchas
* Pipeline code is evaluated to *build a graph*; avoid side effects (no writes, no `display`) in dataset functions.
* `dropDuplicates` on a stream keeps unbounded state; production code bounds it with a watermark.
* Reading a dataset by bare name (`incidents_bronze`) resolves within the pipeline's catalog/schema.
* Run on serverless to avoid cluster setup. The pipeline is triggered, so it stops when the data is processed.
* The event log is a hidden table: query it with `event_log(...)` as the pipeline owner. Metrics exist only for updates that actually processed data, and delivery is best effort.
* When a new column shows up in the source (chapter 03's `source_channel`), a streaming table in a pipeline picks it up and restarts the query itself; you do not see the deliberate failure from chapter 03.
* **Full refresh** clears streaming tables and re-reads the source. That is fine here (the raw files stay in the volume) and a disaster if the source files are gone.
* The key `raw_path` is set under **Settings → Configuration** and read with `spark.conf.get`. Pipeline *parameters* (a Beta feature) are for SQL code only.

## Try it yourself
1. **Warn instead of drop.** Change one `expect_or_drop` to `expect`, run the update, and compare the silver row count and the event log with the original run. Then change it to `expect_or_fail` and explain what the failed update tells you.
2. **Add a quarantine table.** The pipeline throws bad rows away. Add a second streaming table holding the rows that fail at least one rule (the inverse of the rules), as in the quarantine pattern in Microsoft's expectation docs. Does its row count match the event log? Bonus: rewrite `daily_threat_briefing` as `CREATE MATERIALIZED VIEW` in a second, SQL file.
3. **Replay a file, then full refresh.** Copy `part-0000.json` into the raw `incident_reports` folder under a new name, run the update, and watch bronze grow while silver stays at 9,500. Then run once with **Full refresh** and compare what each run does to the materialized view. Delete the copy afterwards, and don't run chapter 03's `ingest()` while it is there, or `shield.bronze.incident_reports` picks it up too.

Bonus: compare the cost (DBUs) of a pipeline update with the notebook version, using the billing system tables from chapter 16.
