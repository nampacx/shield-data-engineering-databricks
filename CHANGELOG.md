# Changelog

## Unreleased
- Repo scaffold, README, story, and synthetic S.H.I.E.L.D. data generator.
- Bicep + azd infrastructure (Databricks, ADLS Gen2, access connector, Key Vault, Event Hubs); default region swedencentral.
- Chapters 00-16: notebooks, docs, declarative pipeline, bundle, CI workflow, runbook, glossary, troubleshooting.
- Notebook quality rules in CLAUDE.md, a `review-notebook` skill, and `scripts/check_notebooks.py` (run in CI and tests).
- All chapters (00-12, 15, 16) follow the notebook quality rules: concept explainers, numbered steps with Goal / Expected and check tables, workspace, clean-up and recap sections, Try-it projects in the docs. Expected numbers are computed from the seeded dataset or stated as expectations; nothing has been run in a workspace yet.
- Chapter 03: `deliver()` takes a target total (safe to re-run), the schema-drift file is the one the generator really puts it in, and `ingest()` waits for the stream. Chapter 16 computes freshness in Spark. Chapter 04 shows the rejected write with an extra column.
- Chapter notebooks have cell ids (nbformat 4.5); `check_notebooks.py` enforces them.
- Quality rules module with unit tests; generator keeps row order so schema drift appears in late files.
