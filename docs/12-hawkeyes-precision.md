# 12 · Hawkeye's precision

**Notebook:** [12_hawkeyes_precision.ipynb](../notebooks/databricks/12_hawkeyes_precision.ipynb)

## Concepts
* **Data skipping**: Delta stores min/max stats per file. If your filter excludes a file's range, the file is never read. Layout decides how well that works.
* **Liquid clustering** (`CLUSTER BY`) co-locates rows by the columns you filter on when `OPTIMIZE` runs, replacing hand-tuned partitioning and Z-ORDER (they cannot be combined with it). Keys can change later with `ALTER TABLE ... CLUSTER BY`; existing data is not rewritten until it is reclustered.
* **Partitioning** is for very large tables with a low-cardinality, always-filtered column (e.g. date). Over-partitioning creates small files. Databricks recommends liquid clustering for new tables.
* **File size**: aim for large files (hundreds of MB); `OPTIMIZE` compacts. Unity Catalog managed tables are tuned automatically.
* **Predictive optimization** runs `OPTIMIZE`, `VACUUM` and `ANALYZE` on managed tables. Learn: on by default for accounts created on or after 11 November 2024, rolled out gradually to older accounts (expected complete by August 2026). Check your account.
* **Joins**: broadcast small tables; avoid skew; filter before joining.
* **Measure**: Query Profile shows files read/pruned, bytes, spill, and the slowest operator.
* **Cost**: DBUs × time. Right-size compute, use serverless/auto-termination, avoid re-running full refreshes.

## What the notebook does
Step 1 generates 500,000 incidents (seed 7, 50 files). Step 2 writes them as a plain table, Step 3 as a table with `CLUSTER BY (location_id, reported_ts)` plus `OPTIMIZE`. Step 4 runs one query on both: the answer must be identical (4,184 incidents and 2,515 casualties for `L003` in March 2025, assuming a UTC session time zone); durations and file counts are shown but never asserted. Step 5 checks that a broadcast join keeps the 500,000 rows and appears in the plan. The clean-up drops the tables and deletes the generated files.

## Method (always the same)
1. Reproduce the slow query. 2. Open its profile. 3. Find the biggest cost (scan, shuffle, skew, spill). 4. Change one thing. 5. Compare the profile.

## Gotchas
* 500k rows is still small (about 120 MB of JSON). Both tables end up with only a few files, maybe one, and then there is nothing to skip. Look at *files pruned* and *bytes read*, not wall-clock seconds, and scale up to see the effect (Try it 3).
* Clustering helps queries that filter on the keys; it does nothing for others.
* The expected counts in the notebook change if you change `INCIDENTS` or the seed: that gives a ❌, not a bug.
* Drop the demo tables afterwards (the notebook's clean-up does).

## Try it yourself
1. Query by `incident_type` only. Is the clustered table still faster? Why or why not?
2. `ALTER TABLE shield.ops.incidents_clustered CLUSTER BY (incident_type)` and re-`OPTIMIZE`. What is the cost of changing keys, and is the old data reclustered?
3. Set `INCIDENTS = 5_000_000` in Step 1 (the clean-up deleted the old files, so it regenerates) and compare the Query Profiles again. Bonus: write the three questions you would ask when someone says "the dashboard is slow".
