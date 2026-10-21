# Databricks notebook source
# MAGIC %md
# MAGIC # 00 · Briefing room
# MAGIC *"I recruit based on potential." — Nick Fury*
# MAGIC
# MAGIC This notebook is a smoke test. It proves your workspace can run code and that you can see the repo.
# MAGIC Read `docs/00-briefing-room.md` first for the concepts.
# MAGIC
# MAGIC **How to run:** connect compute (top right; serverless is fine), then click **Run all**. Needs nothing from earlier chapters.
# MAGIC New to notebooks? Read `docs/how-to-run-notebooks.md` once.
# MAGIC
# MAGIC **What happens:** three tiny checks. 1) Spark runs. 2) You see who and where you are. 3) The repo's own Python code can be imported.

# COMMAND ----------

# MAGIC %md ## 1. Can Spark run?

# COMMAND ----------

# MAGIC %md
# MAGIC `spark` is the entry point to Spark and is already there in every notebook (do not create it yourself). `spark.range(5)` makes a
# MAGIC table with one column `id` and the numbers 0 to 4; we rename the column. `display(...)` shows a DataFrame as a table under the cell.
# MAGIC **Expect:** a table with 5 rows.

# COMMAND ----------

df = spark.range(5).withColumnRenamed("id", "agent_number")
display(df)

# COMMAND ----------

# MAGIC %md ## 2. Which identity and catalog am I using?

# COMMAND ----------

# MAGIC %md
# MAGIC `spark.sql(...)` runs SQL and returns a DataFrame. These three functions tell you which user runs the code, and which Unity Catalog
# MAGIC catalog and schema are used when you write a table name without a prefix. **Expect:** one row. The catalog may be `main` or similar for now; from chapter 01 on we use `shield`.

# COMMAND ----------

display(spark.sql("SELECT current_user() AS me, current_catalog() AS catalog, current_schema() AS schema"))

# COMMAND ----------

# MAGIC %md ## 3. Can I import the repo's code?
# MAGIC This works when the repo is cloned as a **Git folder** in the workspace (Workspace → Create → Git folder).

# COMMAND ----------

# MAGIC %md
# MAGIC Python needs to know where to find the repo's helper package `shield_data` (folder `src/`). The code walks two folders up from the
# MAGIC notebook's folder to find the repo root and adds `src` to the import path. This only works if the notebook runs from the Git folder.
# MAGIC **Expect:** a line like `N S.H.I.E.L.D. locations loaded from /Workspace/...`. `ModuleNotFoundError` means the repo is not a Git folder.

# COMMAND ----------

import os
import sys

repo_root = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
sys.path.insert(0, os.path.join(repo_root, "src"))

from shield_data.generate import make_locations

print(f"{len(make_locations())} S.H.I.E.L.D. locations loaded from {repo_root}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Change `spark.range(5)` into a DataFrame of ten agent codenames and add a column with the codename length.
# MAGIC 2. Find where in the UI you can see the compute this notebook ran on.
