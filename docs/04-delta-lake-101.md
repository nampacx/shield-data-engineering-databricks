# 04 · Delta Lake 101

**Notebook:** [04_delta_lake_101.ipynb](../notebooks/databricks/04_delta_lake_101.ipynb)

## Concepts
* **Delta = Parquet files + a transaction log** (`_delta_log`). Each commit adds a numbered version. That gives you **ACID** transactions (a write is all-or-nothing), **time travel** (chapter 07), and **concurrent-safe** writes. Delta is a table format, and the default one on Azure Databricks.
* **Schema enforcement**: appends that do not match the table are rejected. **Schema evolution** is explicit (`ALTER TABLE ADD COLUMNS`) or automatic when you ask for it (`mergeSchema` on a write).
* **MERGE**: upsert (update matches, insert the rest) in one atomic statement. It is the workhorse of incremental loads. The source must have **one row per key**, or the statement fails with `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE`.
* **Small files problem**: many tiny writes make many tiny files and slow reads. `OPTIMIZE` compacts them. `VACUUM` removes files the log no longer references, after the retention period (7 days default).

## What the notebook does
It opens with a short explainer ("Delta Lake: data files plus a log"), then eight steps, each with a goal, an expected result and a check table:

1. Copy `bronze.agents` into `silver.agents` (50 rows, five columns) and confirm the table format is `delta`.
2. Append a row with an unknown column: the write is rejected and the table is unchanged.
3. Add a `last_seen` column on purpose.
4. `MERGE` one promotion (`A0001`) and one recruit (`A9001`): 51 rows.
5. Read `DESCRIBE HISTORY`: one commit per change, with the `MERGE` metrics.
6. to 8. On a throwaway table: 15 single-row inserts make 15 files, `OPTIMIZE` makes it 1, and a `VACUUM ... DRY RUN` lists nothing because the replaced files are younger than the retention period.

The notebook is standalone: it needs chapter 03's `shield.bronze.agents` and the `shield.silver` schema from chapter 01. It keeps `silver.agents` (chapter 11 uses it) and drops the demo table. Nothing has been run in a workspace yet, so the expected values are expectations.

## Gotchas
* `CREATE OR REPLACE TABLE` keeps history; `DROP` + create does not.
* Don't lower `VACUUM` retention below the longest running query or time-travel need.
* Managed tables: dropping the table deletes data. External tables: it does not.
* On Unity Catalog managed tables Databricks tunes file sizes and can run `OPTIMIZE` and `VACUUM` for you (predictive optimization), so the file counts in Steps 6 to 8 can differ from what the notebook expects. The notebook switches auto compaction off on its demo table to make the effect visible.
* `ALTER TABLE ... ADD COLUMNS` fails if the column already exists, so guard it (the notebook checks first).

## Try it yourself
1. **Duplicate keys.** Make the `USING` side of the `MERGE` hold two rows for `A0001`. What does Delta do, and how would you de-duplicate the source first (for example with `row_number()`)?
2. **Deactivate the missing.** Add `WHEN NOT MATCHED BY SOURCE THEN UPDATE SET active = false` to the `MERGE`, with an update batch that lists only some agents. Which agents get deactivated, and why is a condition on that clause a good idea on a big table?
3. **Compare file counts on real data.** Run `DESCRIBE DETAIL` on `bronze.incident_reports`, then `OPTIMIZE` it, then `DESCRIBE DETAIL` again. How many files before and after, and what does `DESCRIBE HISTORY` say about it?
