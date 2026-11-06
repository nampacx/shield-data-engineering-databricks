# Glossary

| Term | Meaning |
|---|---|
| ACID | Atomic, Consistent, Isolated, Durable: transaction guarantees Delta gives you on files |
| Auto Loader | Streaming file source (`cloudFiles`) that processes only new files |
| Bronze / Silver / Gold | Raw / cleaned / business-ready layers (medallion architecture) |
| Bundle | Declarative Automation Bundle (formerly Asset Bundle): deployable project definition |
| Catalog / Schema | Top two levels of the Unity Catalog namespace: `catalog.schema.table` |
| CDF | Change Data Feed: row-level change records of a Delta table |
| CHECK constraint | Delta rule the table itself enforces on every write; a violating write fails. See [06](06-natasha-spots-the-fake.md) |
| Checkpoint | Saved streaming progress; makes restarts safe |
| Column mask | Function on a column that returns a masked value for users who should not see the real one. See [11](11-governance-vs-hydra.md) |
| Data skipping | Delta uses per-file min/max statistics to skip files a query cannot match. See [12](12-hawkeyes-precision.md) |
| DBU | Databricks Unit: the billing unit for compute consumption |
| Delta Lake | Open table format: Parquet + transaction log |
| Expectation | Pipeline rule on each row (`EXPECT`) that warns, drops the row or fails the update; counted in the event log. See [08](08-declarative-pipelines.md) |
| External location | Unity Catalog object linking a storage path to a storage credential |
| Idempotent | Safe to run more than once with the same result |
| Lakeflow | Databricks' data engineering suite: Jobs, Spark Declarative Pipelines, Connect |
| Liquid clustering | Adaptive data layout (`CLUSTER BY`) that replaces partitioning/Z-ORDER |
| Materialized view | Query result kept up to date, refreshed incrementally when possible |
| Medallion | Layered bronze/silver/gold design |
| MERGE | Atomic upsert statement |
| Metastore | Regional Unity Catalog container for catalogs and permissions |
| Quarantine | Table for rows that failed quality rules |
| Row filter | Function on a table that hides rows from users who should not see them. See [11](11-governance-vs-hydra.md) |
| Shuffle | Moving rows between machines for a `groupBy` or `join`; shows as `Exchange` in the plan. See [02](02-first-recon.md) |
| Streaming table | Table fed incrementally by a streaming query |
| System tables | Read-only tables in the `system` catalog with billing, job and lineage records. See [14](14-project-insight.md) |
| Time travel | Reading a Delta table as of an older version/timestamp |
| Unity Catalog | Governance layer: permissions, lineage, volumes, models |
| Volume | Unity Catalog-governed folder for files |
| Watermark | How late an event may arrive before its window is considered final |
