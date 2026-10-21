# 07 · Doctor Strange's time stone

**Notebook:** [07_doctor_strange_time_stone.py](../notebooks/databricks/07_doctor_strange_time_stone.py)

## Concepts
* **History**: `DESCRIBE HISTORY` lists each version with user, operation, and metrics: a free audit log of writes.
* **Time travel**: `SELECT ... VERSION AS OF n` / `TIMESTAMP AS OF`. Reproduce a report exactly as it was.
* **RESTORE**: roll the table back to an earlier version. It creates a new version; nothing is erased.
* **Change Data Feed (CDF)**: with `delta.enableChangeDataFeed = true`, `table_changes('t', fromVersion)` returns row-level changes with `_change_type` (`insert`, `update_preimage`, `update_postimage`, `delete`). It powers incremental downstream loads and audit trails.

## Limits
* Time travel only reaches back as far as data files still exist: `VACUUM` and log retention (`delta.deletedFileRetentionDuration`, `delta.logRetentionDuration`) decide that.
* CDF only records changes made **after** it is enabled.
* It is not a backup: a dropped table or deleted storage is gone. Plan real backups/replication separately.

## Try it yourself
See the notebook. Bonus: explain to a colleague when you would use time travel vs CDF vs a proper SCD2 history table.
