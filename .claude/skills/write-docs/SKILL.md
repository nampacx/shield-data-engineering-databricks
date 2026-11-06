---
name: write-docs
description: Write or improve a chapter doc or guide in docs/ - TL;DR, big-picture diagram, full concept explanations that match the notebook, a steps table with the notebook's numbers, gotchas, not covered, Try-it projects. Use when asked to create, review or update any .md file in docs/.
---

# Write or review a doc

The rules live in "Writing documentation" in [CLAUDE.md](../../../CLAUDE.md). That section is the single source of truth: read it first and follow it. Don't restate or change the rules here.

## Steps

1. Read the rules, the reference example [docs/05-medallion.md](../../../docs/05-medallion.md), then the chapter's notebook (`notebooks/databricks/NN_*.ipynb`) and the doc you are changing.
2. List the concepts the notebook explains (its opening table and explainer sections). Check each has a full explanation in the doc: idea, picture, how this repo implements it, why, not covered yet, plus the depth the notebook leaves out.
3. Check the doc against the notebook: step numbers, table names, counts, expectations, chapter references, status words (`drafted`, `unverified`, `preview`). Where they differ, the notebook's own tables and code are the source; fix the doc, or fix the notebook if it is wrong, and say which.
4. Write in the structure from the rules. Keep what is already correct; don't rewrite sentences that are fine.
5. Verify any new Databricks or Azure claim against Microsoft Learn before you write it. Mark what you could not verify.
6. Check relative links resolve (`grep -o '](\.\./[^)]*)'` and test the paths) and that mermaid blocks are one flow each.
7. Add a `CHANGELOG.md` line when a reader notices the change.
