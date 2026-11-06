# 03 · Coulson ingests

**Notebook:** [03_coulson_ingests.ipynb](../notebooks/databricks/03_coulson_ingests.ipynb)

## Concepts
* **Landing zone**: files exactly as delivered. Never edit them; they are your replay source.
* **Auto Loader** (`cloudFiles`): a streaming source that remembers which files it has processed (in the checkpoint) and only reads new ones. `trigger(availableNow=True)` = "process everything new, then stop", i.e. incremental **batch** on a schedule. Serverless notebooks and jobs accept only this trigger (and the deprecated `Trigger.Once`).
* **Schema inference and evolution**: Auto Loader stores the inferred schema in `schemaLocation`. With `addNewColumns` (the default when you give no schema), a new field makes the stream stop once with an `UnknownFieldException` after saving the new schema; the next start continues. Other modes: `rescue` (never fail; new columns go to `_rescued_data`), `failOnNewColumns`, `none`.
* **Bronze**: raw plus lineage columns (`_source_file`, `_ingested_at`). No cleaning here. Auto Loader also adds `_rescued_data`.

The notebook has two explainers: "Auto Loader: incremental ingestion into bronze" (paths, trigger, lineage columns) and "Schema drift and schema evolution" (before the failing step).

## What the notebook does
A `deliver()` function simulates files arriving; `ingest()` loads new ones to `shield.bronze.*` and waits for the stream to finish (`awaitTermination()`; `toTable` alone returns immediately). Seven steps with check tables:
1. The three CSV dimension feeds (50 agents, 10 locations, 120 threat assessments).
2. The first incident file: 2,050 rows.
3. A second run with nothing new: still 2,050. That is the checkpoint.
4. Files 2 and 3: 6,150 rows.
5. Files 4 and 5 bring the new field `source_channel`. **One deliberate failure**: the stream stops once.
6. The same call again succeeds: 10,250 rows, 2,045 of them with a `source_channel`.
7. Bronze keeps everything: 250 duplicate IDs, 96 rows without an agent, 110 with the invalid severity `catastrophic`.

The drift starts in the **fourth** file (200 of its 2,050 rows have the field), not only in the last one. That is why the notebook delivers files with `deliver(feed, total=N)` and stops after the third file before Step 5. The numbers assume the chapter 02 dataset and a fresh start; they are expectations, computed from the generator and not from a workspace run. The exact exception name and message of Step 5 are not verified.

Running it again: every cell is safe to repeat (`deliver(..., total=N)` never delivers more than N files, and a finished stream loads nothing), but the counts of a fresh run no longer hold. Use the commented reset cell under Clean up: it drops the bronze tables **and** deletes the landing files and checkpoints, which must go together.

## Gotchas
* Checkpoint and schema paths must be stable and outside the table folder. Delete a checkpoint = reprocess everything.
* Bronze contains duplicates and bad rows **on purpose**. Fixing them there would destroy your audit trail.
* Directory-listing mode is the default; file-events mode scales better but needs extra Azure setup.
* Chapters 08 and 10 use the same landing zone and bronze tables. Do not reset them in the middle of those chapters.

## Try it yourself
1. Copy an already delivered file into `raw/incident_reports` under a new name (for example `part-0000-copy.json`) and run `ingest`. What does Auto Loader do, and how many duplicates does bronze have now? Auto Loader tracks files by path, not by content.
2. Reset the incident feed (see Clean up), switch `schemaEvolutionMode` to `rescue`, redo the deliveries, and look at `_rescued_data` after the drift files. Compare with `failOnNewColumns`: how do you get that stream going again?
3. Ingest `sensor_pings` too with a new bronze table, and compare file count vs. row count. Bonus: ingest the same feed with a `.schema(...)` instead of inference, and compare behaviour on drift.
