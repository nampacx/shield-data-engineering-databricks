# Changelog

## Unreleased
- Repo scaffold, README, story, and synthetic S.H.I.E.L.D. data generator.
- Bicep + azd infrastructure (Databricks, ADLS Gen2, access connector, Key Vault, Event Hubs); default region swedencentral.
- Chapters 00-16: notebooks, docs, declarative pipeline, bundle, CI workflow, runbook, glossary, troubleshooting.
- Notebook quality rules in CLAUDE.md, a `review-notebook` skill, and `scripts/check_notebooks.py` (run in CI and tests).
- Quality rules module with unit tests; generator keeps row order so schema drift appears in late files.
