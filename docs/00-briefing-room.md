# 00 · Briefing room

> "I recruit based on potential." — Nick Fury

**Notebook:** [00_briefing_room.py](../notebooks/databricks/00_briefing_room.py) · **Story:** [story.md](../story.md)

## How to run this chapter

**Before you start:** nothing from earlier chapters. You only need a workspace and the repo as a Git folder (section 1 of [How to run a chapter notebook](how-to-run-notebooks.md)). No catalog or storage setup is needed yet.

**Steps**
1. Open the notebook and connect serverless compute ([How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3).
2. Click **Run all** in the toolbar.
3. Read the output under each cell, then try the two exercises at the bottom.

**What you should see:** a table with 5 rows (`agent_number` 0 to 4), a one-row table with your user name and the current catalog, and a line like `N S.H.I.E.L.D. locations loaded from /Workspace/...`.

If the last cell fails with `ModuleNotFoundError: shield_data`, the repo was not cloned as a Git folder or the notebook was moved out of `notebooks/databricks/`. See [troubleshooting](troubleshooting.md). Safe to re-run any time.

## What a data engineer does
A data engineer builds and runs the systems that move data from where it is created to where decisions are made, and keeps it **correct, fresh, secure, and affordable** on the way. The daily work:

1. **Ingest** data from files, databases, APIs, and event streams.
2. **Transform** it into clean, modelled tables.
3. **Orchestrate** the steps so they run on time, in order, and recover from failure.
4. **Guard quality** so bad data is caught, not trusted.
5. **Govern** who may see what, and where data came from.
6. **Operate** it: monitoring, cost, incidents, deployments.

## The mental model
```
sources → ingest → bronze (raw) → silver (clean) → gold (business-ready) → dashboards / ML
              governed by Unity Catalog, orchestrated by Jobs, deployed as code
```

## Databricks in five lines
* **Workspace**: the web UI and the place where code runs. **Compute**: serverless or clusters that run Spark.
* **Spark**: distributed engine; you describe transformations on DataFrames or SQL.
* **Delta Lake**: table format on cloud storage with transactions, history, and schema control.
* **Unity Catalog**: catalogs → schemas → tables/volumes, with permissions and lineage.
* **Lakeflow**: Jobs (orchestration), Spark Declarative Pipelines (declarative ETL), Connect (ingestion).

## New to notebooks?
Read [How to run a chapter notebook](how-to-run-notebooks.md) once. Every later chapter relies on it.

## Repo tour
`infra/` (Bicep) · `notebooks/databricks/` (chapters) · `pipelines/` (declarative pipeline code) · `resources/` + `databricks.yml` (bundle) · `src/shield_data/` (data generator + quality rules) · `tests/` · `docs/`.

## Cost warning
Compute and Event Hubs cost money. Prefer serverless, stop what you are not using, and run `azd down --purge` when you pause.

## Try it yourself
* Explain the medallion architecture to a friend using a non-data example (a kitchen: delivery, prep, plated dish).
* Find your current employer's "bronze, silver, gold" even if nobody calls them that.
