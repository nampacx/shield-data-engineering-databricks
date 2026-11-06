# 11 · Governance vs Hydra

**Notebook:** [11_governance_vs_hydra.ipynb](../notebooks/databricks/11_governance_vs_hydra.ipynb)

## Concepts
* **Securable hierarchy**: metastore → catalog → schema → table/view/volume/function. Privileges are inherited downward. Access to a table needs `USE CATALOG` + `USE SCHEMA` + `SELECT`.
* **Least privilege by layer**: consumers get gold; engineers get bronze/silver; only pipelines write.
* **Groups, not people**: grant to account-level groups, so onboarding/offboarding is one membership change.
* **Column mask**: function applied when a column is read. **Row filter**: function that hides rows. Both are tied to the table, so they hold in every tool (SQL, notebooks, BI). They only restrict; they never grant access.
* **Tags**: classify data (`pii`, `classification`) so it can be found and policies can target it.
* **Lineage and audit**: automatic table/column lineage in Catalog Explorer; queryable through `system.access.*` once enabled.
* **ABAC (attribute-based access control)**: tag-driven row filter and column mask policies defined once on a catalog or schema. Learn recommends it for many tables. It was **Public Preview** in the November 2025 release notes, so check its status before relying on it. The notebook uses the table-level form and does not cover ABAC.

## What the notebook does
Step 1 looks at the grants on `shield.gold`. Step 2 records the baseline of `shield.silver.agents` (50 agents, 51 after chapter 04's MERGE; 29 with clearance 1 to 3). Steps 3 and 4 add the column mask and the row filter, Step 5 the tags, Step 6 reads lineage from the system table. The clean-up removes the filter, the mask, both functions and the tags, and checks that the table is back to the baseline.
The check tables adapt to whether you are in the group `fury` (the notebook asks `is_account_group_member('fury')`), so they pass for members and non-members alike.

## Grants to try (not run by the notebook)
```sql
GRANT USE CATALOG ON CATALOG shield TO `analysts`;
GRANT USE SCHEMA, SELECT ON SCHEMA shield.gold TO `analysts`;
-- analysts get gold only; engineers keep bronze/silver
-- to undo:
REVOKE USE SCHEMA, SELECT ON SCHEMA shield.gold FROM `analysts`;
REVOKE USE CATALOG ON CATALOG shield FROM `analysts`;
```
Replace `analysts` with a real account-level group.

## Gotchas
* `is_account_group_member()` needs account-level groups (account console), not workspace-local ones.
* Test masks and filters as a user who is *not* in the privileged group. This repo has not verified whether the table owner is exempt from the policies; the notebook measures instead of assuming.
* Drop the policy before you drop its function (`ALTER TABLE ... DROP ROW FILTER`, then `DROP FUNCTION`), otherwise the table becomes unreadable.
* `CREATE OR REPLACE TABLE` keeps an existing row filter and masks on columns with the same name. Leftover policies from an aborted run would follow the table into later chapters.
* The function parameter type must match the column type; otherwise values are cast, and with ANSI mode off failed casts become `NULL`.
* Reading a table with a filter or mask needs a SQL warehouse, standard access mode, or dedicated compute on Databricks Runtime 15.4 LTS or above.
* System schemas are off by default: a metastore admin enables them (`access`, `billing`, `lakeflow`). System lineage can lag behind and only holds lineage the platform could infer.
* Masks and filters add cost to queries; don't stack them everywhere.

## Try it yourself
1. Create the `fury` group, add yourself, and re-run the notebook. Which values in the check tables change?
2. Write a policy for a table you own at work: which columns are PII, who may see them? Express one as a mask function and one as a row filter.
3. Answer from lineage: if `silver.locations` is wrong, which gold tables are affected? Bonus: write a one-page data access policy for S.H.I.E.L.D. (roles → privileges → layers).
