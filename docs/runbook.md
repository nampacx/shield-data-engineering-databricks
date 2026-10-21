# Runbook: shield_daily failed

*For chapter 16. Written for 3 a.m. Keep it short and keep it current.*

## 1. Which task failed?
Jobs & Pipelines → `shield_daily` → latest run. Note the failed task key.

| Task | Typical cause | First action |
|---|---|---|
| `ingest` | Schema drift (new column) | **Repair run**. Auto Loader records the new schema and succeeds on retry. |
| `ingest` | No files / storage permission error | Check `/Volumes/shield/landing/raw/incident_reports`; check the external location grants. |
| `silver` | Bronze table missing or schema changed in a breaking way | Compare `DESCRIBE shield.bronze.incident_reports` with the previous version (`VERSION AS OF`). |
| `gold` | Silver empty or join keys missing | Count rows in `shield.silver.incident_reports` and `shield.silver.locations`. |
| `health_check` | A data check failed (the message names it) | See below. |

## 2. Health-check failures
* `reconciliation`: rows disappeared between bronze and silver+quarantine. Compare counts per `_source_file`.
* `quarantine_rate`: a producer is sending bad data. Group the quarantine table by `failed_rules` and `_source_file`; tell the owner of the feed.
* `gold_freshness`: the gold task did not write. Check the `gold` task output and `DESCRIBE HISTORY`.
* `silver_unique`: duplicates leaked. Re-run `silver` (full overwrite is idempotent).

## 3. Bad data already in gold?
`DESCRIBE HISTORY shield.gold.daily_threat_briefing`, then `RESTORE TABLE ... TO VERSION AS OF <last good>`. Re-run once the cause is fixed.

## 4. Escalate
If you cannot explain the failure in 30 minutes, hand over: link the run, the failed task, what you tried.
