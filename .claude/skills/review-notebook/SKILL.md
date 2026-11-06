---
name: review-notebook
description: Review or improve a chapter notebook (notebooks/databricks/NN_*.ipynb) for learners - standalone cells, chapter template, one experiment per cell with goal and expected outcome, check tables, clean-up and recap. Use when asked to review, refactor, clean up or improve a notebook, or to apply the notebook quality rules to a chapter.
---

# Review a notebook

The rules live in "Notebook quality (the learner's view)" in [CLAUDE.md](../../../CLAUDE.md). That section is the single source of truth: read it first, follow it, and don't restate or change the rules here.

## Steps

1. Read the rules, then `notebooks/databricks/NN_*.ipynb` and its doc `docs/NN-*.md`.
2. Map the notebook before changing it. Print every cell with its index and type, and list:
   - what it needs (tables from earlier chapters, `shield_data` imports, compute, permissions);
   - every name used in more than one cell (parse code cells with `ast`);
   - every concept the notebook uses, and for each: introduced here or in an earlier chapter, and where the notebook explains it;
   - every experiment, and whether it has Goal, input, Expected and a check;
   - what it creates, and whether `🧹 Clean up` removes it.
3. Report findings to the user first, in this order: standalone-ness and prerequisites, template (setup, workspace, clean up, recap), concepts that are used but not explained (or explained twice), experiments, what the reader sees, names, facts. Propose; don't rewrite the whole notebook in one go.
4. For a missing explanation, add a section before the first step that needs it, in the shape the rules give (idea, picture, how this notebook implements it, why, not covered yet), and copy the facts from the notebook's own tables and steps, not from memory. Mirror it in two or three lines in the doc. Change one concern per step. Expected values stay expectations until the user has run the notebook in a workspace; say so and don't claim `verified`.
5. Edit the `.ipynb` as JSON with a small script: find cells by a unique text marker, assert each replacement matches exactly once, keep cell ids, write LF and `indent=1`. Don't touch cells you didn't mean to change.
6. Check: `python scripts/check_notebooks.py`, `ruff check .`, `pytest -q`. Then re-read every markdown cell that describes what you changed and fix what went stale.
7. When the user pastes output, compare it with **Expected:** and find the cause (code, rule or expectation) before changing anything. Say which, with the evidence.
8. Update `CHANGELOG.md`, the chapter doc, `story.md` and the README status row if what the reader sees changed.
