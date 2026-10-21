# 03 · Coulson ingests

**Notebook:** [03_coulson_ingests.py](../notebooks/databricks/03_coulson_ingests.py)

## Concepts
* **Landing zone**: files exactly as delivered. Never edit them; they are your replay source.
* **Auto Loader** (`cloudFiles`): a streaming source that remembers which files it has processed (in the checkpoint) and only reads new ones. `trigger(availableNow=True)` = "process everything new, then stop", i.e. incremental **batch** on a schedule.
* **Schema inference and evolution**: Auto Loader stores the inferred schema in `schemaLocation`. With `addNewColumns`, a new field makes the stream stop once after saving the new schema; the next start continues. Other modes: `rescue` (never fail; unknown data goes to `_rescued_data`), `failOnNewColumns`, `none`.
* **Bronze**: raw plus lineage columns (`_source_file`, `_ingested_at`). No cleaning here.

## What the notebook does
A `deliver()` function simulates files arriving; `ingest()` loads new ones to `shield.bronze.*`. You see: second run does nothing, later deliveries add rows, and the last file triggers schema drift.

## Gotchas
* Checkpoint and schema paths must be stable and outside the table folder. Delete a checkpoint = reprocess everything.
* Bronze contains duplicates and bad rows **on purpose**. Fixing them there would destroy your audit trail.
* Directory-listing mode is the default; file-events mode scales better but needs extra Azure setup.

## Try it yourself
See the notebook. Bonus: ingest the same feed with a `.schema(...)` instead of inference, and compare behaviour on drift.
