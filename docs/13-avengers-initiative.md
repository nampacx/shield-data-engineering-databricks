# 13 · The Avengers Initiative

**Notebook:** [13_avengers_initiative.ipynb](../notebooks/databricks/13_avengers_initiative.ipynb)

> Status: drafted. Nothing here has run in a real workspace yet; the notebook's **Expected** values are expectations, and the dashboard steps (UI) are unverified.

## Concepts
* **Serving layer**: how gold data reaches people and systems. Dashboards (SQL warehouse + AI/BI dashboards), notebooks, BI tools over JDBC/ODBC, APIs, ML models. A role, not a feature: your job is a stable, documented gold table.
* **SQL warehouses**: compute tuned for SQL/BI. Serverless starts in seconds and stops when idle, but bills while it runs.
* **AI/BI dashboards**: a dashboard is a set of *datasets* (SQL queries) plus a canvas of charts. Generally available; the older "legacy" dashboards have reached end of life. Viewers can reach everything a dataset returns, so select only the columns the charts need.
* **Features and label**: a model learns from numeric *features* to predict a *label*. Categories become 0/1 columns (one-hot encoding). The label must not leak into the features.
* **MLflow + Unity Catalog**: track experiments; register models as `catalog.schema.model` with versions, aliases and permissions. A signature is required for Unity Catalog, and `input_example` lets MLflow infer it.
* **Data engineers and ML**: you do not need to be a data scientist, but you own the *features pipeline*: reproducible, tested, versioned data that models train and score on.

## What the notebook does
Five steps, each with a goal and an expected result: it checks the three dashboard queries against the gold tables (365 days, 10 cities with Budapest on top, 4 severities, assuming the chapter-02 dataset and chapter 06), then walks you through building the dashboard in the UI. Next it builds features and a label from silver (9,500 rows, 18 feature columns, 1,863 serious incidents), splits 7,600 / 1,900, trains a random forest, logs the AUC to MLflow and registers `shield.gold.serious_incident_model`. The data is random, so AUC ≈ 0.5 (a stand-in run gave 0.49 to 0.51; the notebook checks 0.45 to 0.55). That honesty is the lesson.

## Feature status (checked against Microsoft Learn, not by running it)
| Feature | Status |
|---|---|
| AI/BI dashboards | Generally available |
| Genie (spaces, now called Genie Agents) | Generally available, but partner-powered AI features must be allowed in the workspace |
| Custom Model Serving, CPU | Listed for Sweden Central; region-dependent. GA or preview for your account: check before promising it |
| MLflow 3 (`name=` in `log_model`) | Documented for Databricks; older MLflow uses `artifact_path=` |

## Cost and clean-up
A running SQL warehouse, a registered model and MLflow runs all stay behind. The notebook's 🧹 Clean up cell deletes the model when you set `CLEAN_UP = True`; stop the warehouse and trash the dashboard yourself.

## Gotchas
* Dashboards query live tables: gold must be stable and documented. A renamed column breaks the charts.
* Never train on a table that is mutated while you read it; use a versioned snapshot (time travel!) and log the version.
* Every run of the training cell registers a **new model version**.
* Model serving endpoints are region-dependent and bill while they are up; check availability before promising one.
* Chapter 06 must have run. After chapter 05 only, silver still holds the 500 defective incidents and the expected numbers differ.

## Try it yourself
1. Make the generator produce a real signal (e.g. more `critical` in one city at night), rebuild silver and gold, and watch the AUC rise. Which feature carries the signal?
2. Refresh the dashboard from the `shield_daily` job with a **dashboard task** after `gold`. What identity refreshes it, and what happens when `gold` fails?
3. Add a feature table with per-location incident counts and join it for training. Which leakage risks appear? Bonus: log the Delta version of the training table as an MLflow tag so you can reproduce the run.
