# 02 · First recon

**Notebook:** [02_first_recon.py](../notebooks/databricks/02_first_recon.py)

## Concepts
* **DataFrame**: a distributed table with a schema. **Transformations** (`filter`, `groupBy`, `join`) are lazy; **actions** (`count`, `display`, `write`) trigger work.
* **SQL and DataFrames are the same engine.** Pick whichever reads better; mix freely with temp views.
* **Narrow vs wide**: `filter`/`select` stay on one partition; `groupBy`/`join` shuffle data across the network, which is where time goes (`Exchange` in `explain()`).
* **Compute**: *serverless* (instant, managed, per-use) vs *classic clusters* (you choose size/runtime). Start with serverless.

## What the notebook does
Generates 10,000 synthetic incidents with 5% defects into the volume `shield.landing.staging`, reads them, aggregates them, and asks you to find the defects by eye.

## Gotchas
* `spark.read.json` infers the schema by reading data: fine here, slow and fragile in production (chapter 03 fixes that).
* Files in volumes are available as ordinary paths (`/Volumes/...`) to Python and to Spark.

## Try it yourself
See the end of the notebook. Bonus: time `count()` on the DataFrame twice. Why is the second no faster? (There is no caching unless you ask for it.)
