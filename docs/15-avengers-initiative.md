# 15 · The Avengers Initiative

**Notebook:** [15_avengers_initiative.py](../notebooks/databricks/15_avengers_initiative.py)

## How to run this chapter

**Before you start:** chapters 05 and 06 are done (gold tables and clean `silver.incident_reports`).

**Steps**
1. Open the notebook and connect serverless compute ([How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3).
2. Run the cell that prints the three dashboard queries and copy them; you will paste them in step 3.
3. Run the model cells. If `import sklearn` or `import mlflow` fails, add a cell with `%pip install scikit-learn mlflow` at the top, run it, and run the notebook again.
4. Dashboard (in the UI): create a SQL warehouse (serverless) if none exists, then create a new dashboard, add each printed query as a dataset, and add a chart for each.

**What you should see:** three printed queries, a line like `AUC = 0.5xx`, and a registered model `shield.gold.serious_incident_model` visible in Catalog Explorer under `shield → gold`.

An AUC near 0.5 is the *correct* result: the data is random. A good pipeline reports that honestly.

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
