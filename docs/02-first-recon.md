# 02 · First recon

**Notebook:** [02_first_recon.ipynb](../notebooks/databricks/02_first_recon.ipynb)

## Concepts
* **DataFrame**: a distributed table with a schema. **Transformations** (`filter`, `groupBy`, `join`) are lazy; **actions** (`count`, `display`, `write`) trigger work.
* **SQL and DataFrames are the same engine.** Pick whichever reads better; mix freely with temp views.
* **Narrow vs wide**: `filter`/`select` stay on one partition; `groupBy`/`join` shuffle data across the network, which is where time goes (`Exchange` in `explain()`).
* **Compute**: *serverless* (instant, managed, per-use) vs *classic clusters* (you choose size/runtime). Start with serverless.

The notebook opens with a short explainer ("How Spark reads your question") that covers the same ideas with a picture of lazy plan, narrow and wide steps.

## What the notebook does
Seven steps, each with a goal, an expected result and a check table:
1. Generates the synthetic feeds into the volume `shield.landing.staging` (10,000 incidents plus 250 replayed duplicates = 10,250 rows, 5% of the incidents with exactly one defect).
2. Reads the incident JSON and checks the inferred schema (nine columns, alphabetical, `reported_at` still text).
3. Runs an action (`count`, `display`) to show the difference between a plan and a result.
4. Groups by incident type and severity (30 groups; the largest is `surveillance` / `low`, 895 incidents).
5. Repeats the aggregation in SQL through a temp view and proves both results are identical.
6. Counts the planted defects (missing agent 96, invalid severity 110, negative casualties 96, unparsable timestamp 99, future timestamp 110), all counted on rows, duplicates included.
7. Finds the 250 incident IDs that were delivered twice.

The numbers are expectations for the seeded dataset (`seed=42`, `dirty=0.05`); they were computed from the generator, not from a workspace run. Nothing is stored apart from the seed data in staging, so there is nothing to clean up, and regenerating overwrites the same files.

## Gotchas
* `spark.read.json` infers the schema by reading data: fine here, slow and fragile in production (chapter 03 fixes that).
* Files in volumes are available as ordinary paths (`/Volumes/...`) to Python and to Spark.
* The "future timestamp" defects are planted relative to the day you generate the data (30 to 400 days ahead). Data generated long ago may show a different count in Step 6.

## Try it yourself
1. Join incidents with `agents/agents.csv` (read it with `header=True`) and list the five busiest codenames. The incident feed has 51 distinct `agent_id` values: 50 agents and `NULL`. What does your join do with the `NULL` rows?
2. Use `explain()` on `by_type` and find the shuffle (`Exchange`) in the plan. Then add a `filter` before the `groupBy` and see which step moves.
3. Step 6 counts 99 rows with an unparsable `reported_at`. Count the distinct incidents instead (expected: 97, from the generator) and explain the difference. Bonus: time `count()` twice. Why is the second no faster? (There is no caching unless you ask for it.)
