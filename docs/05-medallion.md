# 05 · Medallion

**Notebook:** [05_medallion.py](../notebooks/databricks/05_medallion.py)

## The layers
| Layer | Contains | Rule of thumb |
|---|---|---|
| **Bronze** | Raw data as received + metadata | Append-only, never "fix" |
| **Silver** | Typed, deduplicated, validated, conformed | One row per business entity/event; the trustworthy base |
| **Gold** | Aggregates and models shaped for a use case | Named after the question it answers |

Why layers? Debuggability (compare layers to find where a number went wrong), reprocessing (rebuild silver from bronze), and separation of concerns (engineers own bronze/silver, analysts consume gold).

## What the notebook does
Builds `silver.incident_reports` (typed timestamp, latest record per `incident_id`), `silver.locations`, and two gold tables: `daily_threat_briefing`, `location_risk`.

## The deliberate flaw
Silver here has no quality gate, so impossible values reach gold. You are meant to notice (the last cell shows `catastrophic` severities). Chapter 06 fixes it.

## Gotchas
* Full refresh (`overwrite`) is simple and idempotent but costs more as data grows; chapter 08 makes it incremental.
* Model gold tables for consumers, not for symmetry with silver.

## Try it yourself
See the notebook. Bonus: decide which layer a "customer lifetime value" table belongs in and justify it.
