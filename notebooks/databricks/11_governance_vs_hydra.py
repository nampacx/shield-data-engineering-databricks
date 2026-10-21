# Databricks notebook source
# MAGIC %md
# MAGIC # 11 · Governance vs Hydra
# MAGIC *Hydra tries to read what it should not.*
# MAGIC
# MAGIC Unity Catalog gives you: privileges (GRANT), row filters, column masks, tags, and lineage.
# MAGIC The group `fury` below must exist as an **account-level group** (account console → User management → Groups).
# MAGIC Until it exists the masking still runs: everybody is simply treated as "not Fury".
# MAGIC Needs `shield.silver.agents` from chapter 04.
# MAGIC
# MAGIC **How to run:** connect serverless compute, then **Run all**. Make sure the last cleanup cells run.
# MAGIC
# MAGIC **Needs:** chapters 04 and 05 done (`shield.silver.agents`, `shield.gold.daily_threat_briefing`). The account-level group `fury` is optional; without it everybody counts as "not Fury".
# MAGIC
# MAGIC **What happens:** four ways Unity Catalog controls data: privileges (`GRANT`), a **column mask** (hide codenames), a **row filter** (hide high-clearance agents) and **tags** (label sensitive columns). Then you look at lineage.
# MAGIC The cleanup at the end removes the mask and filter so later chapters see real data. If the run stops earlier, run the two `DROP` statements yourself.

# COMMAND ----------

# MAGIC %md ## 1. Privileges: least privilege by layer

# COMMAND ----------

# MAGIC %md
# MAGIC **Privileges.** Access to a table needs `USE CATALOG` + `USE SCHEMA` + `SELECT`. The `GRANT` lines are comments because your groups do not exist yet; replace `analysts` with a real group to try them.
# MAGIC The only live statement lists who has access to `gold`. **Expect:** a table of grants (maybe only the owner).

# COMMAND ----------

# Replace with real groups. Shown as comments so the notebook runs without them:
# GRANT USE CATALOG ON CATALOG shield TO `analysts`;
# GRANT USE SCHEMA, SELECT ON SCHEMA shield.gold TO `analysts`;
# (analysts get gold only; engineers keep bronze/silver)
display(spark.sql("SHOW GRANTS ON SCHEMA shield.gold"))

# COMMAND ----------

# MAGIC %md ## 2. Column mask: only Fury sees real codenames

# COMMAND ----------

# MAGIC %md
# MAGIC A **column mask** is a function applied whenever the column is read. `is_account_group_member('fury')` is true only for members of that account-level group. Everyone else sees `*** CLASSIFIED ***`.
# MAGIC **Expect:** masked codenames (unless you are in `fury`). The mask applies in every tool, not just this notebook.

# COMMAND ----------

spark.sql(
    """
    CREATE OR REPLACE FUNCTION shield.gold.mask_codename(codename STRING)
    RETURN CASE WHEN is_account_group_member('fury') THEN codename ELSE '*** CLASSIFIED ***' END
    """
)
spark.sql("ALTER TABLE shield.silver.agents ALTER COLUMN codename SET MASK shield.gold.mask_codename")
display(spark.sql("SELECT agent_id, codename, clearance_level FROM shield.silver.agents LIMIT 5"))

# COMMAND ----------

# MAGIC %md ## 3. Row filter: you only see agents at or below your clearance
# MAGIC Here only `fury` members see clearance 4-5 agents.

# COMMAND ----------

# MAGIC %md
# MAGIC A **row filter** decides which rows a reader may see. Non-`fury` readers get clearance 1–3 only. **Expect:** counts for fewer clearance levels than before.

# COMMAND ----------

spark.sql(
    """
    CREATE OR REPLACE FUNCTION shield.gold.clearance_filter(clearance INT)
    RETURN is_account_group_member('fury') OR clearance <= 3
    """
)
spark.sql("ALTER TABLE shield.silver.agents SET ROW FILTER shield.gold.clearance_filter ON (clearance_level)")
display(spark.sql("SELECT clearance_level, COUNT(*) AS agents FROM shield.silver.agents GROUP BY 1 ORDER BY 1"))

# COMMAND ----------

# MAGIC %md ## 4. Tags: make sensitive data discoverable

# COMMAND ----------

# MAGIC %md
# MAGIC **Tags** classify data so it can be found and policies can target it. The query reads them back from the catalog's `information_schema`. **Expect:** two rows for `codename`: `classification=secret` and `pii=true`.

# COMMAND ----------

spark.sql("ALTER TABLE shield.silver.agents ALTER COLUMN codename SET TAGS ('classification' = 'secret', 'pii' = 'true')")
display(spark.sql("SELECT * FROM shield.information_schema.column_tags WHERE table_name = 'agents'"))

# COMMAND ----------

# MAGIC %md ## 5. Lineage and audit
# MAGIC In Catalog Explorer open `shield.gold.daily_threat_briefing` → **Lineage** to see upstream tables.
# MAGIC The same data is queryable from system tables once a metastore admin enables the `access` schema
# MAGIC (`system.access.table_lineage`, `system.access.audit`).

# COMMAND ----------

# MAGIC %md
# MAGIC **Lineage** tells you which tables feed which. It is recorded automatically; in Catalog Explorer open a table → **Lineage**. This cell reads the same data from system tables, which a metastore admin must enable first.
# MAGIC **Expect:** rows, or the message `System tables not enabled yet`.

# COMMAND ----------

try:
    display(
        spark.sql(
            """
            SELECT source_table_full_name, target_table_full_name, event_time
            FROM system.access.table_lineage
            WHERE target_table_full_name LIKE 'shield.%'
            ORDER BY event_time DESC LIMIT 20
            """
        )
    )
except Exception as e:  # noqa: BLE001
    print("System tables not enabled yet:", type(e).__name__)

# COMMAND ----------

# MAGIC %md ## Clean up the policies (so later chapters see real data)

# COMMAND ----------

# MAGIC %md
# MAGIC **Cleanup:** removes the row filter and the mask. Do not skip this, or later chapters will see masked agents.

# COMMAND ----------

spark.sql("ALTER TABLE shield.silver.agents DROP ROW FILTER")
spark.sql("ALTER TABLE shield.silver.agents ALTER COLUMN codename DROP MASK")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it yourself
# MAGIC 1. Create the `fury` group, add yourself, and re-run sections 2 and 3. What changes?
# MAGIC 2. Write a policy for a table you own at work: which columns are PII, who may see them?
# MAGIC 3. Answer from lineage: if `silver.locations` is wrong, which gold tables are affected?
