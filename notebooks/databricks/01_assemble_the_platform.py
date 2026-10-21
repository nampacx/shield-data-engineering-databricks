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

# COMMAND ----------

dbutils.widgets.text("storage_account", "", "Storage account name (azd output STORAGE_ACCOUNT_NAME)")
dbutils.widgets.text("credential", "shield_cred", "Storage credential name")
sa = dbutils.widgets.get("storage_account")
cred = dbutils.widgets.get("credential")
assert sa, "Fill in the storage_account widget"

# COMMAND ----------

# MAGIC %md ## External location → catalog

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

for schema in ["landing", "bronze", "silver", "gold", "ops"]:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS shield.{schema}")

spark.sql("CREATE VOLUME IF NOT EXISTS shield.landing.staging COMMENT 'Generated seed data'")
spark.sql("CREATE VOLUME IF NOT EXISTS shield.landing.raw COMMENT 'Files arriving from the field'")
spark.sql("CREATE VOLUME IF NOT EXISTS shield.landing.checkpoints COMMENT 'Streaming checkpoints and schemas'")

# COMMAND ----------

display(spark.sql("SHOW SCHEMAS IN shield"))

# COMMAND ----------

display(spark.sql("SHOW VOLUMES IN shield.landing"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Create an *external* volume on the `landing` container (second external location) and compare it with the managed volume.
# MAGIC 2. Run `DESCRIBE CATALOG EXTENDED shield` and find the managed location.
# MAGIC 3. Add a `sandbox` schema and grant a colleague `USE SCHEMA` + `CREATE TABLE` on it only.
