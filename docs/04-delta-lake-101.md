# 04 · Delta Lake 101

**Notebook:** [04_delta_lake_101.py](../notebooks/databricks/04_delta_lake_101.py)

## Concepts
* **Delta = Parquet files + a transaction log** (`_delta_log`). Each commit adds a version. That gives you **ACID** transactions, **time travel** (chapter 07), and **concurrent-safe** writes.
* **Schema enforcement**: appends that do not match the table are rejected. **Schema evolution** is explicit (`ALTER TABLE ADD COLUMNS`, or `mergeSchema`).
* **MERGE**: upsert (update matches, insert the rest) in one atomic statement. It is the workhorse of incremental loads. The source must have **one row per key**, or the statement fails.
* **Small files problem**: many tiny writes make many tiny files and slow reads. `OPTIMIZE` compacts them. `VACUUM` removes unreferenced files after the retention period (7 days default).

## What the notebook does
Copies `bronze.agents` into `silver.agents`, tries a bad write, evolves the schema, merges promotions and recruits, inspects `DESCRIBE HISTORY`, and shows OPTIMIZE reducing 15 files to 1.

## Gotchas
* `CREATE OR REPLACE TABLE` keeps history; `DROP` + create does not.
* Don't lower `VACUUM` retention below the longest running query or time-travel need.
* Managed tables: dropping the table deletes data. External tables: it does not.

## Try it yourself
See the notebook. Bonus: read `_delta_log` JSON files in the table's folder (use `DESCRIBE DETAIL` for the location) and match them to `DESCRIBE HISTORY`.
