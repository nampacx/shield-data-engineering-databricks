# 06 · Natasha spots the fake

**Notebook:** [06_natasha_spots_the_fake.ipynb](../notebooks/databricks/06_natasha_spots_the_fake.ipynb) · **Rules:** [quality.py](../src/shield_data/quality.py)

## Concepts
* **Data quality dimensions**: validity (is the value allowed?), completeness (is it present?), uniqueness, timeliness, consistency.
* **Rules as data**: a dictionary `name → SQL expression`, defined once in `src/shield_data/quality.py` and reused by the notebook, the pipeline, and the tests.
* **Quarantine pattern**: failing rows are stored with the *names of the rules they failed*, not deleted. Operations can then answer "which feed is sending garbage, and what kind?"
* **Fail vs quarantine vs warn**: fail the job when the whole batch is untrustworthy; quarantine when single rows are bad; warn when you only want a metric.
* **Constraints** (`NOT NULL`, `CHECK`) make the *table* refuse bad writes: the last line of defence.

**In the notebook:** the section "Quality rules, quarantine and CHECK constraints" (before Step 1) explains these three ideas with the exact tables used. Rules and quarantine are patterns you follow, nothing in Databricks enforces them; a CHECK constraint is a Delta feature that makes the table itself reject a violating write, and adding one can upgrade the table's writer protocol.

## What the notebook does
Five steps, each with a goal, an expected result and a check table. It parses timestamps safely (`try_to_timestamp`) and evaluates the rules (valid 9,739 rows, invalid 511). Valid rows go to silver (9,500 incidents) and invalid ones to `silver.incident_reports_quarantine`. It counts failures per rule, rebuilds the gold tables on clean data, then adds a CHECK constraint that the table enforces. The notebook is standalone: it needs chapter 03's bronze tables, not chapter 05.

## Tests
`tests/test_quality.py` proves every injected defect is caught and, if `pyspark` is installed, that the Spark SQL rules agree with the Python mirror. This is how you unit-test data logic without a cluster.

## Gotchas
* NULL in a SQL condition is neither true nor false: use `coalesce(..., false)` so NULL counts as failure.
* Rules reflect business agreements; get them from the data owner, not from guessing.

## Try it yourself
1. Add a rule: `agent_id` must exist in `silver.agents`. Which rows fail now? Add it to `quality.py`, run `pytest`, and see which test tells you to update the Python mirror.
2. Turn the quarantine counts into a daily quality table in `shield.ops` (rule, date, failed_rows).
3. Decide: for which rule would you rather *fail the job* than quarantine? Why?
