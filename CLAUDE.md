# Conventions

- Learning repo for Azure Databricks data engineering, Marvel / S.H.I.E.L.D. themed. Fabric is out of scope (separate repo).
- Chapter `NN` = `notebooks/databricks/NN_<slug>.py` (Databricks source format) + `docs/NN-<slug>.md` + a section in `story.md` + a row in the README status table.
- Every chapter doc ends with a "Try it yourself" section of 2–3 mini-projects.
- Verify Databricks and Azure syntax against Microsoft Learn before writing it. Never claim `verified` in the README unless the chapter ran in a real workspace.
- The only dataset is the synthetic one from `src/shield_data`. No external downloads.
- Python 3.11+, `ruff` for lint, `pytest` for tests. Keep helpers in `src/shield_data` importable and tested.
- Infra is Bicep + azd under `infra/`. Never commit secrets; use `.env` (see `.env.example`).
- Tone: friendly and story-driven, honest about preview features and rough edges.
