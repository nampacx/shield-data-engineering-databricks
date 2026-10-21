# 11 · Governance vs Hydra

**Notebook:** [11_governance_vs_hydra.py](../notebooks/databricks/11_governance_vs_hydra.py)

## How to run this chapter

**Before you start:** chapters 04 and 05 are done (`shield.silver.agents` and `shield.gold.daily_threat_briefing` exist). The `fury` group is optional: without it everyone is simply treated as not-Fury.

**Steps**
1. Open the notebook and connect serverless compute ([How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3).
2. Click **Run all**, or step section by section to see the effect of each policy.
3. In section 2 compare the codenames before and after the mask; in section 3 compare the counts per clearance level.
4. Make sure the last cleanup cell runs: it removes the mask and the filter so later chapters see real data.

**What you should see:** codenames shown as `*** CLASSIFIED ***`, only clearance 1 to 3 agents visible, tag rows from `column_tags`, and either lineage rows or the message `System tables not enabled yet`.

If a run stops before the cleanup cell, run the two cleanup statements yourself. Otherwise `silver.agents` keeps its mask and filter.

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
