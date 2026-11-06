# 00 · Briefing room

> "I recruit based on potential." — Nick Fury

**Notebook:** [00_briefing_room.ipynb](../notebooks/databricks/00_briefing_room.ipynb) · **Story:** [story.md](../story.md)

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

## Repo tour
`infra/` (Bicep) · `notebooks/databricks/` (chapters) · `pipelines/` (declarative pipeline code) · `resources/` + `databricks.yml` (bundle) · `src/shield_data/` (data generator + quality rules) · `tests/` · `docs/`.

## What the notebook does
Three small steps, each with a check table: Spark answers (`spark.range(5)`), you see your user and default catalog, and the notebook imports `shield_data` from the repo's `src/` folder. It creates nothing, so there is nothing to clean up.

Two things to know before you start:
* `spark` and `display` are already defined in every Databricks notebook; the compute you attach to (serverless is simplest) runs your cells.
* The repo must be a **Git folder** (Workspace → Create → Git folder), so that `../../src` sits next to the notebook. Public repositories can be cloned without Git credentials; private ones and pushes need a personal access token or OAuth set up under your Git provider settings.

## Cost warning
Compute and Event Hubs cost money. Prefer serverless, stop what you are not using, and run `azd down --purge` when you pause.

## Try it yourself
1. In the notebook, turn `spark.range(5)` into a DataFrame of ten agent codenames with a column for the codename length. (`spark.createDataFrame` with a list of tuples is enough.)
2. Find where in the UI you can see the compute the notebook ran on, and what else you can switch it to.
3. Explain the medallion architecture to a friend with a non-data example (a kitchen: delivery, prep, plated dish), then find your employer's "bronze, silver, gold" even if nobody calls them that.
