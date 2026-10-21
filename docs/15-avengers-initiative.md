# 15 · The Avengers Initiative

**Notebook:** [15_avengers_initiative.py](../notebooks/databricks/15_avengers_initiative.py)

## Concepts
* **Serving layer**: how gold data reaches people and systems. Dashboards (SQL warehouse + Dashboards), notebooks, BI tools over JDBC/ODBC, APIs, ML models.
* **SQL warehouses**: compute tuned for SQL/BI. Serverless starts in seconds and stops when idle.
* **MLflow + Unity Catalog**: track experiments; register models as `catalog.schema.model` with versions, aliases, and permissions.
* **Data engineers and ML**: you do not need to be a data scientist, but you own the *features pipeline*: reproducible, tested, versioned data that models train and score on.

## What the notebook does
Prints three dashboard queries to paste into a new Dashboard, then trains a random forest on silver incidents and registers it as `shield.gold.serious_incident_model`. The data is random, so AUC ≈ 0.5. That honesty is the lesson.

## Gotchas
* Dashboards query live tables: gold must be stable and documented.
* Never train on a table that is mutated while you read it; use a versioned snapshot (time travel!) and log the version.
* Model serving endpoints are region-dependent; check availability before promising one.

## Try it yourself
See the notebook. Bonus: log the Delta version of the training table as an MLflow tag so you can reproduce the run.
