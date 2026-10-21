# 10 · Maria Hill schedules

**Notebook:** [10_maria_hill_schedules.py](../notebooks/databricks/10_maria_hill_schedules.py)

## How to run this chapter

**Before you start:** chapters 03 to 06 are done (bronze incidents, `silver.locations`, and the quality rules), because the three steps rebuild silver and gold.

**Steps**
1. Open the notebook and connect serverless compute. First try it **by hand**: run the cell that creates the widgets, use the **Pipeline step** dropdown to pick `ingest`, and run the cells below it (**Run All Below**). Repeat for `silver`, then `gold`. Each run prints `step '...' done`.
2. Now automate it: **Jobs & Pipelines → Create → Job**, name `shield_daily`, and add three *Notebook* tasks that point to this notebook with the parameter `step=ingest`, `step=silver`, `step=gold`. Set `silver` to depend on `ingest` and `gold` on `silver`.
3. Set retries to 2, add a failure notification, add a schedule and leave it **paused**, then click **Run now**.
4. Run the job a second time and compare the tables: they must be identical.

**What you should see:** three green tasks in the job's run page, and unchanged table contents after the second run. That sameness is idempotency.

The `deliver_files` widget sets how many raw files the `ingest` step copies in per run (default 1).

## Concepts
* **Lakeflow Jobs**: orchestrate *tasks* (notebooks, pipelines, SQL, Python wheels, dashboards, other jobs) with dependencies, parameters, retries, schedules/triggers, and notifications.
* **Idempotency**: running a task twice gives the same result as once. This is what makes **retries** and **repair runs** safe. Techniques: overwrite derived tables from their source; `MERGE` on a business key; skip already-delivered files; `replaceWhere` for partitions.
* **Parameters** make one notebook serve many tasks and environments.
* **Failure design**: retries for transient errors, alerts for human-needed errors, and a *repair run* to resume from the failed task rather than start over.
* **Triggers**: cron schedule, file arrival, table update, or continuous.

## Job shape
```
ingest → silver → gold → (chapter 16) health_check
```
The same job is defined as code in `resources/shield_job.yml` (chapter 13).

## Gotchas
* Time zones: set `timezone_id` explicitly.
* Create schedules **paused** while learning, otherwise they keep spending.
* Don't pass big data between tasks; pass table names. Use task values only for small signals.

## Try it yourself
See the notebook. Bonus: sketch the dependency graph for a nightly load of 10 source systems with one shared dimension table.
