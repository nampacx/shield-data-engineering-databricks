# 16 · Project Insight (capstone)

**Notebook:** [16_project_insight.py](../notebooks/databricks/16_project_insight.py) · **Runbook:** [runbook.md](runbook.md)

## How to run this chapter

**Before you start:** all earlier chapters are done, at least up to chapter 10 (silver, quarantine and gold tables exist and gold was written recently).

**Steps**
1. Open the notebook and connect serverless compute ([How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3).
2. Click **Run all**.
3. Read the `PASS` / `FAIL` lines. The system-table queries are optional and print a message if the schemas are not enabled.
4. Then follow the **Do this** list below to break something on purpose and fix it with the runbook.

**What you should see:** four `PASS` lines and `All checks passed.` at the end.

If any check shows `FAIL`, the last cell **raises an error on purpose**. In a job this is how the alert fires, so a red run is the notebook working, not breaking.

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
| Health checks + alerts | notebook 16 as last task |
| Cost visibility | `system.billing.usage` query in notebook 16 |
| Runbook | [runbook.md](runbook.md) |

## Do this
1. Deploy the bundle (chapter 13) and run `shield_daily`.
2. Break something on purpose (deliver a file with an extra column, a bad timestamp, an empty file). Watch which check catches it.
3. Fix it using only the runbook.
4. Write your **5-minute walkthrough**: sources → layers → quality → orchestration → governance → cost → what fails and how you know. This is your interview story.

## Production gaps (be honest in the interview)
* Auth uses personal login and a connection string; production uses service principals / managed identity.
* No network isolation (private endpoints, VNet injection).
* Single environment's data; no data contracts with producers.
* Monitoring stops at a failing job; no dashboards on freshness SLAs.

## Try it yourself
Pick a dataset from your current or target employer and design the same platform on paper in one page.
