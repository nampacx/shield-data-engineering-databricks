# Changelog

## Unreleased
- Repo scaffold, README, story, and synthetic S.H.I.E.L.D. data generator.
- Bicep + azd infrastructure (Databricks, ADLS Gen2, access connector, Key Vault, Event Hubs); default region swedencentral.
- Chapters 00-14: notebooks, docs, declarative pipeline, bundle, CI workflow, runbook, glossary, troubleshooting.
- Notebook quality rules in CLAUDE.md, a `review-notebook` skill, and `scripts/check_notebooks.py` (run in CI and tests).
- All chapters (00-14) follow the notebook quality rules: concept explainers, numbered steps with Goal / Expected and check tables, workspace, clean-up and recap sections, Try-it projects in the docs. Expected numbers are computed from the seeded dataset or stated as expectations; nothing has been run in a workspace yet.
- Chapter 03: `deliver()` takes a target total (safe to re-run), the schema-drift file is the one the generator really puts it in, and `ingest()` waits for the stream. Chapter 14 computes freshness in Spark. Chapter 04 shows the rejected write with an extra column.
- Chapters 13 (infrastructure as code) and 14 (CI/CD) became one unnumbered guide, `docs/deploy-and-automate.md`; The Avengers Initiative is now chapter 13 and Project Insight chapter 14, so notebook and doc numbers match and have no gaps.
- Notebooks 01, 09 and 10 create their widgets in a cell of their own, before the cell that reads them, so the first run no longer fails on an empty widget.
- Chapter 03: `deliver()` also prints which files the raw landing zone holds, so an empty "delivered []" is explained (already delivered on an earlier run).
- Chapter notebooks have cell ids (nbformat 4.5); `check_notebooks.py` enforces them.
- Quality rules module with unit tests; generator keeps row order so schema drift appears in late files.
