# Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `azd up` fails on role assignments | You lack Owner/User Access Administrator on the subscription | Ask for the role, or have an admin deploy once |
| `PERMISSION_DENIED: CREATE STORAGE CREDENTIAL` | Not a metastore admin | Account admin: Catalog → your metastore → set yourself (or a group) as admin |
| `CREATE CATALOG` fails with a storage error | External location/credential missing or connector lacks role | Check `SHOW EXTERNAL LOCATIONS`; check the connector's *Storage Blob Data Contributor* role |
| `ModuleNotFoundError: shield_data` | Repo not cloned as a Git folder, or notebook not in `notebooks/databricks/` | Clone via Workspace → Git folder; the notebooks add `../../src` to `sys.path` |
| Auto Loader: `UnknownFieldException` | Expected once after schema drift | Re-run; use a Job retry in production |
| `[CAST_INVALID_INPUT]` on timestamps | Used `to_timestamp` on a bad value under ANSI mode | Use `try_to_timestamp` |
| `table_changes` fails | CDF not enabled before that version | Enable it, then query versions after the enable |
| Kafka source not found / not allowed | Serverless limits | Use classic job compute for chapter 09 part B |
| `system.*` table not found | System schema not enabled | Metastore admin enables `access`, `billing`, `lakeflow` |
| Bundle validate complains about a field | CLI/schema version difference | `databricks bundle schema` and adjust; check the docs for your CLI version |
| Unexpected bill | Event Hubs or idle compute | `azd down --purge`; check `system.billing.usage` |
