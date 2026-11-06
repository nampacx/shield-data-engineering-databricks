# 05 · Medallion

**Notebook:** [05_medallion.ipynb](../notebooks/databricks/05_medallion.ipynb)

## The layers
| Layer | Contains | Rule of thumb |
|---|---|---|
| **Bronze** | Raw data as received + metadata | Append-only, never "fix" |
| **Silver** | Typed, deduplicated, validated, conformed | One row per business entity/event; the trustworthy base |
| **Gold** | Aggregates and models shaped for a use case | Named after the question it answers |

Why layers? Debuggability (compare layers to find where a number went wrong), reprocessing (rebuild silver from bronze), and separation of concerns (engineers own bronze/silver, analysts consume gold).

## How this repo implements it
* One Unity Catalog schema per layer: `shield.bronze`, `shield.silver`, `shield.gold`. The table name stays the same across layers (`incident_reports`).
* Each layer reads only the one before it: silver reads bronze, gold reads silver. Gold never reads bronze.
* Silver transforms rows (parse the timestamp, keep the newest record per key). Gold is a `GROUP BY` named after the question it answers.
* The medallion is a pattern, not a feature. Nothing enforces the layers except naming and team discipline.

The notebook opens with the same picture and walks through it.

## What the notebook does
Five steps, each with a goal, an expected result and a check table: silver incidents (typed timestamp, latest record per `incident_id`: 10,250 bronze rows become 10,000), `silver.locations`, and the gold tables `daily_threat_briefing` and `location_risk`. It ends by counting the defects that got through.

## The deliberate flaw
Silver here has no quality gate, so impossible values reach gold. Step 5 counts 500 defective incidents in silver, among them 109 with the non-existent severity `catastrophic`. Chapter 06 fixes it.

## Gotchas
* Full refresh (`CREATE OR REPLACE`) is simple and idempotent but costs more as data grows; chapter 08 makes it incremental.
* Model gold tables for consumers, not for symmetry with silver.

## Try it yourself
1. Add `gold.agent_workload`: incidents per agent codename (join `silver.agents`). Which agents have no incidents?
2. Run the silver step twice. Why is the result identical, and which part of the cell makes it so?
3. Sketch what each layer would hold for a retail dataset you know. Which layer does a "customer lifetime value" table belong in?
