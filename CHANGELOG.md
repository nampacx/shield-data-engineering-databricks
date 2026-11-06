# Changelog

## Unreleased
- Repo scaffold, README, story, and synthetic S.H.I.E.L.D. data generator.
- Bicep + azd infrastructure (Databricks, ADLS Gen2, access connector, Key Vault, Event Hubs); default region swedencentral.
- Chapters 00-16: notebooks, docs, declarative pipeline, bundle, CI workflow, runbook, glossary, troubleshooting.
- Notebook quality rules in CLAUDE.md, a `review-notebook` skill, and `scripts/check_notebooks.py` (run in CI and tests).
- Chapters 05 and 06 follow the notebook quality rules: numbered steps with Goal / Expected and check tables, workspace, clean-up and recap sections. Numbers are computed from the seeded dataset, not yet run in a workspace.
- Chapter notebooks have cell ids (nbformat 4.5); `check_notebooks.py` enforces them.
- Quality rules module with unit tests; generator keeps row order so schema drift appears in late files.
