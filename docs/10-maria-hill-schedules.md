# 10 · Maria Hill schedules

**Notebook:** [10_maria_hill_schedules.py](../notebooks/databricks/10_maria_hill_schedules.py)

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
