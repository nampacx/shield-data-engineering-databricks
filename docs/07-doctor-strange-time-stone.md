# 07 · Doctor Strange's time stone

**Notebook:** [07_doctor_strange_time_stone.ipynb](../notebooks/databricks/07_doctor_strange_time_stone.ipynb)

## Concepts
* **History**: `DESCRIBE HISTORY` lists each version with user, operation, and metrics: a free audit log of writes (kept 30 days by default).
* **Time travel**: `SELECT ... VERSION AS OF n` / `TIMESTAMP AS OF`. Reproduce a report exactly as it was.
* **RESTORE**: roll the table back to an earlier version. It creates a new version; nothing is erased.
* **Change Data Feed (CDF)**: with `delta.enableChangeDataFeed = true`, `table_changes('t', fromVersion, toVersion)` returns row-level changes with `_change_type` (`insert`, `update_preimage`, `update_postimage`, `delete`). It powers incremental downstream loads and audit trails. Newer runtimes (Databricks Runtime 19 or above) also have an *automatic* change data feed based on row tracking that needs no table property; the two cannot be combined and the notebook uses the property.

## What the notebook does
It opens with a short explainer, then seven steps with a goal, an expected result and a check table each. It needs `shield.silver.incident_reports` from chapter 06 (9,500 incidents, 435 of them `critical`); with no table or no `critical` rows the setup cell stops with a message.

1. Turn on the change feed and remember the known-good version.
2. "Hydra" downgrades the 435 `critical` incidents to `low` with an `UPDATE`.
3. Find the commit in `DESCRIBE HISTORY` (operation, user, `numUpdatedRows`).
4. List the changed rows with `table_changes`: 435 `update_preimage` and 435 `update_postimage` rows.
5. Read the old snapshot with `VERSION AS OF`.
6. `RESTORE` the table to the known-good version.
7. Check that the history now ends in `RESTORE` on top of `UPDATE`: the tampering is still visible.

The table ends with the data it started with. The clean-up switches the change feed off again, but the extra versions stay in the history. The expected values are expectations: the notebook has not been run in a workspace yet. If you stop between steps 2 and 6 the table stays tampered; re-running chapter 06 rebuilds it.

## Limits
* Time travel only reaches back as far as data files still exist: `VACUUM` and the table properties `delta.deletedFileRetentionDuration` (default 7 days) and `delta.logRetentionDuration` (default 30 days) decide that. Recent Databricks Runtime versions block time travel to versions older than the file retention period.
* CDF only records changes made **after** it is enabled, and `VACUUM` removes its files too.
* It is not a backup: a dropped table or deleted storage is gone. Plan real backups/replication separately.
* `RESTORE` rewrites the table's current state, so a streaming job reading the table can see the restored rows as new data.

## Try it yourself
1. **Ask by time.** Repeat Step 5 with `TIMESTAMP AS OF` instead of a version number. Pick a timestamp from `DESCRIBE HISTORY` and one just before the tampering. What changes if you pick a time earlier than the table's first version?
2. **Build an audit table.** Use the change feed of the tampering commit to create `shield.silver.incident_audit` with `incident_id`, old severity, new severity and `_commit_timestamp`. Hint: self-join the pre- and post-images on `incident_id`. How would you keep it up to date as more changes arrive?
3. **See what VACUUM does to time travel.** On a throwaway table (never on a shared one), update a few rows, run `VACUUM ... RETAIN 0 HOURS`, then try `VERSION AS OF` the earlier version. You need a classic cluster for this: it requires turning off `spark.databricks.delta.retentionDurationCheck.enabled`, which serverless compute does not let you change. Explain to a colleague when you would use time travel, the change feed, or a proper slowly changing dimension (SCD2) history table.
