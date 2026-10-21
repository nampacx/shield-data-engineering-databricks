# Databricks notebook source
# MAGIC %md
# MAGIC # 00 · Briefing room
# MAGIC *"I recruit based on potential." — Nick Fury*
# MAGIC
# MAGIC This notebook is a smoke test. It proves your workspace can run code and that you can see the repo.
# MAGIC Read `docs/00-briefing-room.md` first for the concepts.

# COMMAND ----------

# MAGIC %md ## 1. Can Spark run?

# COMMAND ----------

df = spark.range(5).withColumnRenamed("id", "agent_number")
display(df)

# COMMAND ----------

# MAGIC %md ## 2. Which identity and catalog am I using?

# COMMAND ----------

display(spark.sql("SELECT current_user() AS me, current_catalog() AS catalog, current_schema() AS schema"))

# COMMAND ----------

# MAGIC %md ## 3. Can I import the repo's code?
# MAGIC This works when the repo is cloned as a **Git folder** in the workspace (Workspace → Create → Git folder).

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
