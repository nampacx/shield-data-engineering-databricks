# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Assemble the platform
# MAGIC *Hill requisitions the base.*
# MAGIC
# MAGIC `azd up` already created the workspace, storage, and access connector. This notebook creates the
# MAGIC **Unity Catalog** objects on top: external location, catalog, schemas, and volumes.
# MAGIC
# MAGIC **Before running**, create the storage credential `shield_cred` (see `docs/01-assemble-the-platform.md`).
# MAGIC You need the `CREATE EXTERNAL LOCATION` and `CREATE CATALOG` privileges (metastore admin has both).
# MAGIC
# MAGIC **How to run:** connect compute, run the first code cell (it creates the boxes), fill the `storage_account` box, then run the rest *from the `assert` cell downward* (cell menu → **Run All Below**). Details below.
# MAGIC
# MAGIC **Needs:** `azd up` finished and the storage credential `shield_cred` created (docs, step 4).
# MAGIC
# MAGIC **What happens:** it creates the Unity Catalog building blocks on top of the Azure storage: an *external location* (permission to use a
# MAGIC storage container), the catalog `shield`, five schemas (`landing`, `bronze`, `silver`, `gold`, `ops`) and three volumes (folders for files).
# MAGIC Safe to re-run: everything uses `IF NOT EXISTS`.

# COMMAND ----------

# MAGIC %md
# MAGIC **Widgets** are input boxes. The first code cell below only *creates* two of them: `storage_account` (you must fill it in) and `credential` (leave `shield_cred`).
# MAGIC The boxes appear in the widget panel, at the top of the notebook or at that cell. The cell after it *reads* them. They are separate cells on purpose, so you can fill the box between the two.
# MAGIC
# MAGIC 1. Run the first code cell (the one with `dbutils.widgets.text`). The two boxes appear.
# MAGIC 2. In a terminal run `azd env get-values` and copy the value of `STORAGE_ACCOUNT_NAME` (only the name, no `https://`).
# MAGIC 3. Paste it into the `storage_account` box and press Enter.
# MAGIC 4. Run the next code cell (the one with `assert`). It passes once the box is filled. Then continue downward with **Run All Below** from that cell's run menu. Avoid **Run all** from the top once the box is filled: it re-runs the cell that creates the widgets, and may reset what you typed.
# MAGIC
# MAGIC No box visible? **Edit → Add parameter**, name `storage_account`, type *Text*.

# COMMAND ----------

dbutils.widgets.text("storage_account", "", "Storage account name (azd output STORAGE_ACCOUNT_NAME)")
dbutils.widgets.text("credential", "shield_cred", "Storage credential name")

# COMMAND ----------

# MAGIC %md
# MAGIC **Step 2:** fill the `storage_account` box, then run the cell below. It reads the boxes and stops with `Fill in the storage_account widget` if the name is missing.

# COMMAND ----------

sa = dbutils.widgets.get("storage_account")
cred = dbutils.widgets.get("credential")
assert sa, "Fill in the storage_account widget"

# COMMAND ----------

# MAGIC %md ## External location → catalog

# COMMAND ----------

# MAGIC %md
# MAGIC **External location:** tells Unity Catalog "this storage container may be used, with this credential". **Catalog:** the top-level
# MAGIC container for our data. `MANAGED LOCATION` is where its managed tables and volumes physically live (the `uc-managed` container).
# MAGIC A permission error here usually means `shield_cred` is missing or you lack `CREATE EXTERNAL LOCATION` / `CREATE CATALOG`.

# COMMAND ----------

spark.sql(
    f"""
    CREATE EXTERNAL LOCATION IF NOT EXISTS shield_managed
    URL 'abfss://uc-managed@{sa}.dfs.core.windows.net/'
    WITH (STORAGE CREDENTIAL `{cred}`)
    """
)
spark.sql(
    f"""
    CREATE CATALOG IF NOT EXISTS shield
    MANAGED LOCATION 'abfss://uc-managed@{sa}.dfs.core.windows.net/shield'
    COMMENT 'S.H.I.E.L.D. intelligence platform'
    """
)

# COMMAND ----------

# MAGIC %md ## Schemas = the medallion layers + landing + ops

# COMMAND ----------

# MAGIC %md
# MAGIC A **schema** is a folder of tables inside a catalog. We create one per medallion layer plus `landing` (arriving files) and `ops` (utility tables).
# MAGIC A **volume** is a governed folder for *files*: `staging` holds the generated seed data, `raw` is where files "arrive", `checkpoints` stores streaming state.
# MAGIC Files in a volume have normal paths like `/Volumes/shield/landing/raw/...`.

# COMMAND ----------

for schema in ["landing", "bronze", "silver", "gold", "ops"]:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS shield.{schema}")

spark.sql("CREATE VOLUME IF NOT EXISTS shield.landing.staging COMMENT 'Generated seed data'")
spark.sql("CREATE VOLUME IF NOT EXISTS shield.landing.raw COMMENT 'Files arriving from the field'")
spark.sql("CREATE VOLUME IF NOT EXISTS shield.landing.checkpoints COMMENT 'Streaming checkpoints and schemas'")

# COMMAND ----------

# MAGIC %md
# MAGIC **Check:** you should see `landing`, `bronze`, `silver`, `gold`, `ops` (plus `default` and `information_schema`, which Unity Catalog adds itself).

# COMMAND ----------

display(spark.sql("SHOW SCHEMAS IN shield"))

# COMMAND ----------

# MAGIC %md
# MAGIC **Check:** three volumes: `staging`, `raw`, `checkpoints`. You can also browse them in **Catalog** in the left sidebar → `shield`.

# COMMAND ----------

display(spark.sql("SHOW VOLUMES IN shield.landing"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Create an *external* volume on the `landing` container (second external location) and compare it with the managed volume.
# MAGIC 2. Run `DESCRIBE CATALOG EXTENDED shield` and find the managed location.
# MAGIC 3. Add a `sandbox` schema and grant a colleague `USE SCHEMA` + `CREATE TABLE` on it only.
