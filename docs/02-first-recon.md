# 02 · First recon

**Notebook:** [02_first_recon.py](../notebooks/databricks/02_first_recon.py)

## How to run this chapter

**Before you start:** chapter 01 is done, so the `shield` catalog and the volume `shield.landing.staging` exist.

**Steps**
1. Open the notebook and connect serverless compute ([How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3).
2. Click **Run all**. The first code cell generates 10,000 incidents and writes them as files into the volume; the rest reads and explores them.
3. Stop at *Spot the mess* and look at the three tables before reading on: these are the defects the next chapters fix.

**What you should see:** a dictionary of row counts per feed from the first cell, the inferred schema, sample rows, and two aggregate tables (DataFrame version and SQL version) with identical numbers.

Safe to re-run: the generator rewrites the same files (fixed seed 42). Chapter 03 needs these files, so do not skip this chapter.

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
