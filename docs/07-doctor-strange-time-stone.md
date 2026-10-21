# 07 · Doctor Strange's time stone

**Notebook:** [07_doctor_strange_time_stone.py](../notebooks/databricks/07_doctor_strange_time_stone.py)

## How to run this chapter

**Before you start:** chapter 06 is done (`shield.silver.incident_reports` exists in its clean form).

**Steps**
1. Open the notebook and connect serverless compute ([How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3).
2. Run the cells **in order with Shift+Enter**: the notebook tampers with a table and then repairs it, and you want to see each state.
3. After *Hydra tampers*, look at the severity table, then follow the audit, the change feed, time travel and `RESTORE`.

**What you should see:** no `critical` rows after the tampering, the update visible in `DESCRIBE HISTORY`, row-level `update_preimage` / `update_postimage` rows, the old counts via `VERSION AS OF`, and the original counts back after `RESTORE`.

If a run stops halfway (after the tampering, before `RESTORE`), the table stays tampered. Run the `RESTORE` cell, or re-run chapter 06 to rebuild it.

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
