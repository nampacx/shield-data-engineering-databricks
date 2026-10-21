# 12 · Hawkeye's precision

**Notebook:** [12_hawkeyes_precision.py](../notebooks/databricks/12_hawkeyes_precision.py)

## How to run this chapter

**Before you start:** chapters 02 and 05 are done (`shield.silver.locations` exists). This notebook generates a bigger dataset and takes noticeably longer than the others.

**Steps**
1. Open the notebook and connect serverless compute ([How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3).
2. Click **Run all** and be patient during the first cell (500,000 incidents are generated once).
3. Compare the two timings printed under *Same query, two layouts*, then open the **Query Profile** for both queries (query history → a query → *See query profile*) and compare files read and bytes read.
4. When finished, drop the demo tables (see the last exercise).

**What you should see:** `numFiles` for the plain and the clustered table, two timings, and, in the profile, fewer files read for the clustered table.

Timings in a notebook are noisy. Trust the profile, not the stopwatch. The demo tables live in `shield.ops` and cost storage until you drop them.

## Concepts
* **Data skipping**: Delta stores min/max stats per file. If your filter excludes a file's range, the file is never read. Layout decides how well that works.
* **Liquid clustering** (`CLUSTER BY`) co-locates rows by the columns you filter on, replacing hand-tuned partitioning and Z-ORDER. Keys can change later without rewriting everything at once.
* **Partitioning** is for very large tables with a low-cardinality, always-filtered column (e.g. date). Over-partitioning creates small files.
* **File size**: aim for large files (hundreds of MB); `OPTIMIZE` compacts.
* **Joins**: broadcast small tables; avoid skew; filter before joining.
* **Measure**: Query Profile shows files read/pruned, bytes, spill, and the slowest operator.
* **Cost**: DBUs × time. Right-size compute, use serverless/auto-termination, avoid re-running full refreshes.

## Method (always the same)
1. Reproduce the slow query. 2. Open its profile. 3. Find the biggest cost (scan, shuffle, skew, spill). 4. Change one thing. 5. Compare the profile.

## Gotchas
* 500k rows is still small. Look at *files pruned* and *bytes read*, not wall-clock seconds.
* Clustering helps queries that filter on the keys; it does nothing for others.
* Drop the demo tables afterwards.

## Try it yourself
See the notebook. Bonus: write the three questions you would ask when someone says "the dashboard is slow".
