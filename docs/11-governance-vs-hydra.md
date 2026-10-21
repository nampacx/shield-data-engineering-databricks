# 11 · Governance vs Hydra

**Notebook:** [11_governance_vs_hydra.py](../notebooks/databricks/11_governance_vs_hydra.py)

## Concepts
* **Securable hierarchy**: metastore → catalog → schema → table/view/volume/function. Privileges are inherited downward. Access to a table needs `USE CATALOG` + `USE SCHEMA` + `SELECT`.
* **Least privilege by layer**: consumers get gold; engineers get bronze/silver; only pipelines write.
* **Groups, not people**: grant to account-level groups, so onboarding/offboarding is one membership change.
* **Column mask**: function applied when a column is read. **Row filter**: function that hides rows. Both are tied to the table, so they hold in every tool (SQL, notebooks, BI).
* **Tags**: classify data (`pii`, `classification`) so it can be found and policies can target it.
* **Lineage and audit**: automatic table/column lineage in Catalog Explorer; queryable through `system.access.*` once enabled.

## Gotchas
* `is_account_group_member()` needs account-level groups (account console), not workspace-local ones.
* Test masks and filters as a user who is *not* in the privileged group; check the docs for who is exempt from policies before trusting a test run as owner.
* System schemas are off by default: a metastore admin enables them (`access`, `billing`, `lakeflow`).
* Masks and filters add cost to queries; don't stack them everywhere.

## Try it yourself
See the notebook. Bonus: write a one-page data access policy for S.H.I.E.L.D. (roles → privileges → layers).
