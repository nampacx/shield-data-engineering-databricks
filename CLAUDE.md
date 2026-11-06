# Conventions

- Learning repo for Azure Databricks data engineering, Marvel / S.H.I.E.L.D. themed. Fabric is out of scope (separate repo).
- Chapter `NN` = `notebooks/databricks/NN_<slug>.ipynb` (Jupyter format so GitHub renders it; Databricks imports it natively) + `docs/NN-<slug>.md` + a section in `story.md` + a row in the README status table.
- Every chapter doc ends with a "Try it yourself" section of 2–3 mini-projects.
- Verify Databricks and Azure syntax against Microsoft Learn before writing it. Never claim `verified` in the README unless the chapter ran in a real workspace.
- The only dataset is the synthetic one from `src/shield_data`. No external downloads.
- Python 3.11+, `ruff` for lint, `pytest` for tests. Keep helpers in `src/shield_data` importable and tested.
- Infra is Bicep + azd under `infra/`. Never commit secrets; use `.env` (see `.env.example`).
- Tone: friendly and story-driven, honest about preview features and rough edges.

# Notebook quality (the learner's view)

Read this before you create or change a notebook. If your tool supports skills, use `review-notebook` ([.claude/skills/review-notebook/SKILL.md](.claude/skills/review-notebook/SKILL.md)); it runs these rules as a checklist.

**Standalone notebooks**
- Each notebook runs on its own. Keep its helper code inline, in the cell that first needs it. No `%run`, no shared notebook-helper modules, no copying one notebook's state into another's via files that only that notebook makes.
- It may import `shield_data` (the synthetic dataset and quality rules in `src/shield_data`) and read tables earlier chapters built. Name those prerequisites in the opening cell, and say how to create them if the reader skipped the chapter.
- If shared notebook code ever becomes worth it, add it as one clearly marked "shared code" section first. Don't spread it across modules.

**Chapter template**
1. `# NN · Title`, the story hook, a table of the concepts it teaches, a link to the doc, and what it needs (earlier chapters, compute, permissions).
2. A setup cell.
3. Numbered sections `## 1 · …`.
4. `## 👀 In the workspace` (skip when there is nothing to see): Catalog Explorer, the Jobs run page, the pipeline graph.
5. `## 🧹 Clean up`: drop what the chapter created, unless the next chapter needs it. Say so when there is nothing to delete.
6. `## 🎯 Recap`, ending with `> 💡 Next: …`. The "Try it yourself" mini-projects stay in the doc.

**One experiment per cell**
- Each experiment gets a markdown cell with `### Step N · Title`, then **Goal:** (what it proves), the input (table, file, query) and **Expected:** (the concrete outcome), then one short code cell.
- Order experiments so each changes one thing. Let the first cell of a sequence create the state it needs. Re-running a cell must not change its result; when it would, say so in the markdown.
- End an experiment with a small check table: result next to expected (✅ / ❌ only where there is a right answer), built from the data (row counts, schema, rule outcomes), not typed by hand.

**What the reader sees**
- The committed notebook has no outputs, so it must read well on GitHub: show one example of the output (a few rows, a schema) in the markdown.
- Show whole results; don't truncate a table with `limit` unless the markdown says why.
- A cell ends with a `display(...)` or nothing, never a raw object repr.

**Names and facts**
- Names used in more than one cell say what they hold (`bronze_incidents`, `silver_incidents`), no `df2`, `tmp`, `x`; none embed a chapter number.
- Mark preview features as preview in the notebook, the doc and the story.
- **Expected:** is an expectation until the notebook ran in a real workspace. After a live run, write down what it showed. Don't mark a chapter `verified` before that.
- After every change to code or output, re-read each markdown cell that describes it. They go stale silently.
- Before a commit, run `python scripts/check_notebooks.py`: no outputs, no execution counts, every code cell parses.
- Add a `CHANGELOG.md` line for every change a reader notices.
