# Databricks notebook source
# MAGIC %md
# MAGIC # 15 · The Avengers Initiative
# MAGIC *The gold layer finally has customers.*
# MAGIC
# MAGIC Two consumers: **dashboards** (Databricks SQL) and a **model** (MLflow). The data is random, so the model will
# MAGIC be useless. That is the point: the plumbing is what you are learning, and a pipeline that reports "AUC ≈ 0.5"
# MAGIC honestly is a good pipeline.
# MAGIC
# MAGIC **How to run:** connect serverless compute and **Run all**. The dashboard part is done in the UI afterwards.
# MAGIC
# MAGIC **Needs:** chapters 05 and 06 done (gold tables and the clean `silver.incident_reports`).
# MAGIC
# MAGIC **What happens:** gold data gets two consumers. 1) Three SQL queries to paste into a Databricks **dashboard**. 2) A small machine-learning model, tracked with **MLflow** and registered in Unity Catalog.
# MAGIC The data is random, so the model scores about AUC 0.5 (no better than a coin flip). That is the honest result, not a bug.

# COMMAND ----------

# MAGIC %md ## 1. Dashboard datasets
# MAGIC Create a SQL warehouse (serverless) and a new **Dashboard**. Use these queries as datasets:

# COMMAND ----------

# MAGIC %md
# MAGIC These cells print three SQL queries. Create a **SQL warehouse** (serverless) and a new **Dashboard**, add each query as a dataset, and build a chart for each. Dashboards query live tables, which is why gold must stay stable.

# COMMAND ----------

QUERIES = {
    "incidents_by_day": "SELECT report_date, SUM(incidents) AS incidents FROM shield.gold.daily_threat_briefing GROUP BY 1 ORDER BY 1",
    "risk_by_city": "SELECT city, serious_incidents, incidents FROM shield.gold.location_risk ORDER BY serious_incidents DESC",
    "severity_mix": "SELECT severity, SUM(incidents) AS incidents FROM shield.gold.daily_threat_briefing GROUP BY 1",
}
for name, q in QUERIES.items():
    print(f"-- {name}\n{q}\n")

# COMMAND ----------

# MAGIC %md ## 2. A model that predicts serious incidents

# COMMAND ----------

# MAGIC %md
# MAGIC Feature preparation. We select a few columns from silver, turn the severity into a 0/1 label `serious`, one-hot encode the text columns with `get_dummies`, and split the data into training (80%) and test (20%) sets.
# MAGIC `toPandas()` pulls the data into the driver's memory: fine for small data, never do it with big tables. If `import` fails, add a cell `%pip install scikit-learn mlflow` and restart.

# COMMAND ----------

import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

pdf = spark.sql(
    """
    SELECT location_id, incident_type, hour(reported_ts) AS hour, dayofweek(reported_ts) AS dow,
           CASE WHEN severity IN ('high','critical') THEN 1 ELSE 0 END AS serious
    FROM shield.silver.incident_reports
    """
).toPandas()

X = pd.get_dummies(pdf.drop(columns="serious"), columns=["location_id", "incident_type"])
y = pdf["serious"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# COMMAND ----------

# MAGIC %md
# MAGIC Trains a random forest, measures **AUC** on the held-out test data (0.5 = no signal, 1.0 = perfect) and logs the metric and the model with **MLflow**.
# MAGIC `databricks-uc` stores the model in Unity Catalog as `shield.gold.serious_incident_model` with versions and permissions. **Expect:** `AUC = 0.5xx`, and the model under **Catalog → shield → gold**.

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")
with mlflow.start_run(run_name="serious_incident_rf"):
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42).fit(X_train, y_train)
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    mlflow.log_metric("auc", auc)
    mlflow.sklearn.log_model(
        model, name="model", input_example=X_train.head(5), registered_model_name="shield.gold.serious_incident_model"
    )
print(f"AUC = {auc:.3f}  (about 0.5 = no signal, as expected for synthetic random data)")

# COMMAND ----------

# MAGIC %md ## 3. Where would this go next?
# MAGIC * Score new incidents in a job task and write predictions to `shield.gold.incident_scores`.
# MAGIC * Serve the model on a serving endpoint (region availability: Sweden Central supports CPU serving).
# MAGIC * Ask questions in plain English with **Genie** on the gold tables (optional, check availability in your workspace).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Make the generator produce a real signal (e.g. more `critical` in one city at night) and watch AUC rise.
# MAGIC 2. Schedule the dashboard refresh from the `shield_daily` job (dashboard task).
# MAGIC 3. Add a feature table with per-location incident counts and join it for training. Which leakage risks appear?
