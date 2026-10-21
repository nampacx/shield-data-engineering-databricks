# Glossary

For how these pieces fit together, see [Core concepts](core-concepts.md).

| Term | Meaning |
|---|---|
| ACID | Atomic, Consistent, Isolated, Durable: transaction guarantees Delta gives you on files |
| Auto Loader | Streaming file source (`cloudFiles`) that processes only new files |
| Bronze / Silver / Gold | Raw / cleaned / business-ready layers (medallion architecture) |
| Bundle | Declarative Automation Bundle (formerly Asset Bundle): deployable project definition |
| Catalog / Schema | Top two levels of the Unity Catalog namespace: `catalog.schema.table` |
| CDF | Change Data Feed: row-level change records of a Delta table |
| Checkpoint | Saved streaming progress; makes restarts safe |
| Delta Lake | Open table format: Parquet + transaction log |
| DBU | Databricks Unit: the billing unit for compute consumption |
| External location | Unity Catalog object linking a storage path to a storage credential |
| Idempotent | Safe to run more than once with the same result |
| Lakeflow | Databricks' data engineering suite: Jobs, Spark Declarative Pipelines, Connect |
| Liquid clustering | Adaptive data layout (`CLUSTER BY`) that replaces partitioning/Z-ORDER |
| Materialized view | Query result kept up to date, refreshed incrementally when possible |
| Medallion | Layered bronze/silver/gold design |
| MERGE | Atomic upsert statement |
| Metastore | Regional Unity Catalog container for catalogs and permissions |
| Quarantine | Table for rows that failed quality rules |
| Streaming table | Table fed incrementally by a streaming query |
| Time travel | Reading a Delta table as of an older version/timestamp |
| Unity Catalog | Governance layer: permissions, lineage, volumes, models |
| Volume | Unity Catalog-governed folder for files |
| Watermark | How late an event may arrive before its window is considered final |
