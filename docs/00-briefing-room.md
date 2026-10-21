# 00 · Briefing room

> "I recruit based on potential." — Nick Fury

**Notebook:** [00_briefing_room.py](../notebooks/databricks/00_briefing_room.py) · **Story:** [story.md](../story.md)

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

## Cost warning
Compute and Event Hubs cost money. Prefer serverless, stop what you are not using, and run `azd down --purge` when you pause.

## Try it yourself
* Explain the medallion architecture to a friend using a non-data example (a kitchen: delivery, prep, plated dish).
* Find your current employer's "bronze, silver, gold" even if nobody calls them that.
