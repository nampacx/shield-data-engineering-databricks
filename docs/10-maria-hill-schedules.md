# 10 · Maria Hill schedules

**Notebook:** [10_maria_hill_schedules.ipynb](../notebooks/databricks/10_maria_hill_schedules.ipynb)

## Concepts
* **Lakeflow Jobs**: orchestrate *tasks* (notebooks, pipelines, SQL, Python wheels, dashboards, other jobs) with dependencies, parameters, retries, schedules/triggers, and notifications.
* **Idempotency**: running a task twice gives the same result as once. This is what makes **retries** and **repair runs** safe. Jobs does not do this for you: a repair re-runs a failed task from its beginning. Techniques: overwrite derived tables from their source; `MERGE` on a business key; skip already-delivered files; `replaceWhere` for partitions.
* **Parameters** make one notebook serve many tasks and environments. The notebook reads them with `dbutils.widgets.get`.
* **Failure design**: retries for transient errors, alerts for human-needed errors, and a *repair run* (jobs with two or more tasks) to resume from the failed task rather than start over. Job-level notifications are not sent for failed attempts that are retried; use task notifications for that.
* **Triggers**: cron schedule, file arrival, table update, or continuous.

## What the notebook does
One notebook, three job tasks. The widget `step` (`ingest`, `silver`, `gold`, or `all` for a run by hand) picks the work. Steps 1 to 3 run the steps and check their results (bronze 10,250 rows, silver 9,500, quarantine 511, gold 8,803 rows over 9,500 incidents). Step 4 runs silver and gold a second time and compares the counts. Step 5 creates the job in the UI and runs it twice. The numbers assume the chapter 02 dataset and a complete chapter 03.

## Job shape
```
ingest → silver → gold → (chapter 16) health_check
```
The same job is defined as code in `resources/shield_job.yml` (chapter 13). It differs from the UI steps in two ways: it sets `max_retries: 2` on the first three tasks only (not on `health_check`) and it has no notifications.

## Gotchas
* Time zones: set `timezone_id` explicitly.
* Create schedules **paused** while learning, otherwise they keep spending.
* Don't pass big data between tasks; pass table names. Use task values only for small signals.
* Don't block a job task on `awaitTermination()`: the Jobs service already waits for running streams. The notebook only waits when you run it by hand with `step = all`.
* After chapter 03 the ingest step finds nothing new. That is the point: it is safe to run again.
* The notebook finds `shield_data` through a relative path from the notebook folder. If a job task cannot import it, Learn warns that the working directory of serverless tasks is not guaranteed; run the notebook from a Git folder or add the `src` folder to the path explicitly.

## Try it yourself
1. Make the job fail on purpose (rename `shield.silver.locations`), confirm the notification, then fix it and use **Repair run**. Which tasks were re-run, and which were not?
2. Add a task-level *condition*: only run `gold` if `silver` produced more than 0 rows.
3. Replace the `silver` full overwrite with an incremental `MERGE`. What must stay true for retries to be safe? Bonus: sketch the dependency graph for a nightly load of 10 source systems with one shared dimension table.
