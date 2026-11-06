# 14 · Project Insight (capstone)

**Notebook:** [14_project_insight.ipynb](../notebooks/databricks/14_project_insight.ipynb) · **Runbook:** [runbook.md](runbook.md)

> Status: drafted. Nothing here has run in a real workspace yet; the notebook's **Expected** values are expectations.

## Goal
A platform you can **hand over**: it loads on a schedule, protects its consumers from bad data, tells you when it is unhealthy, and explains how to fix it.

## The checklist
| Area | Where it lives |
|---|---|
| Infrastructure as code | `infra/`, `databricks.yml` |
| Ingestion with drift handling | notebook 03 / pipeline |
| Quality gates + quarantine | `quality.py`, notebook 06 |
| Orchestration with retries | `shield_daily` job |
| Governance | notebook 11 |
| Tests + CI | `tests/`, `ci.yml` |
| Health checks + alerts | notebook 14 as last task |
| Cost visibility | `system.billing.usage` query in notebook 14 |
| Runbook | [runbook.md](runbook.md) |

## What the notebook does
It is the `health_check` task of `shield_daily`, run after `gold` with no parameters. It only reads. Four checks, each its own step:

| Check | Passes when |
|---|---|
| `reconciliation` | silver + distinct quarantined incidents ≥ 99 % of distinct bronze incidents (10,000 = 9,500 + 500 with the chapter-02 dataset) |
| `quarantine_rate` | under 15 % of incidents are quarantined (5.0 % expected) |
| `gold_freshness` | `gold.daily_threat_briefing` changed less than 24 hours ago |
| `silver_unique` | no `incident_id` appears twice in silver |

A fifth step prints DBUs per day and job outcomes from the system tables (`system.billing.usage`, `system.lakeflow.job_run_timeline`) and never fails the task. The last step shows the summary and raises one `RuntimeError` naming every failed check, which fails the task and fires the job's notification.

## Dependencies and failure modes
* It needs the bronze, silver, quarantine and gold tables from chapters 03, 05/06 and 10. If one is missing, Setup stops with `Missing tables`. That also fails the job, but it means "could not check"; the runbook tells the two apart.
* `gold_freshness` fails by design when you run the notebook by hand days after the gold task. Run the `gold` step first.
* System tables need a metastore admin to enable the `lakeflow` schema and grant `SELECT`; records lag by up to about 12 hours (billing) or one hour (jobs). Without access, Step 5 prints a message and moves on.
* The thresholds (99 %, 15 %, 24 h) are choices for this synthetic data. Rehearse a failure without touching data by setting `QUARANTINE_RATE_LIMIT = 0.01` in Setup.
* Running the job costs DBUs. The schedule is deployed paused. Tear everything down with `azd down --purge` and `databricks bundle destroy` when you finish.

## Run it
1. Deploy the bundle (see the [deploy guide](deploy-and-automate.md)) and run `shield_daily`. The guide says its bundle files have not been validated with the CLI, so expect to fix field names.
2. Open the `health_check` task of the run and read the summary table.
3. Break something on purpose (see mini-project 1) and fix it using only the runbook.

## Production gaps (be honest in the interview)
* Auth uses personal login and a connection string; production uses service principals / managed identity.
* No network isolation (private endpoints, VNet injection).
* Single environment's data; no data contracts with producers.
* Monitoring stops at a failing job; no dashboards on freshness SLAs.

## Try it yourself
1. Break each check on purpose and confirm the failure message tells you where to look: delete some rows from silver (reconciliation), deliver a file full of bad timestamps (quarantine rate), duplicate a silver row (uniqueness), wait out the freshness window. Fix each one using only the runbook.
2. Write the 5-minute walkthrough of this platform: sources → layers → quality → orchestration → governance → cost → what fails and how you know. Or pick a dataset from your current or target employer and design the same platform on paper in one page.
3. Add a check for schema drift (a new column in bronze that silver does not know about). Should it fail the task or only warn?
