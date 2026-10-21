# 06 · Natasha spots the fake

**Notebook:** [06_natasha_spots_the_fake.py](../notebooks/databricks/06_natasha_spots_the_fake.py) · **Rules:** [quality.py](../src/shield_data/quality.py)

## Concepts
* **Data quality dimensions**: validity (is the value allowed?), completeness (is it present?), uniqueness, timeliness, consistency.
* **Rules as data**: a dictionary `name → SQL expression`, defined once in `src/shield_data/quality.py` and reused by the notebook, the pipeline, and the tests.
* **Quarantine pattern**: failing rows are stored with the *names of the rules they failed*, not deleted. Operations can then answer "which feed is sending garbage, and what kind?"
* **Fail vs quarantine vs warn**: fail the job when the whole batch is untrustworthy; quarantine when single rows are bad; warn when you only want a metric.
* **Constraints** (`NOT NULL`, `CHECK`) make the *table* refuse bad writes: the last line of defence.

## What the notebook does
Parses timestamps safely (`try_to_timestamp`), evaluates the rules, writes valid rows to silver and invalid ones to `silver.incident_reports_quarantine`, then adds a CHECK constraint.

## Tests
`tests/test_quality.py` proves every injected defect is caught and, if `pyspark` is installed, that the Spark SQL rules agree with the Python mirror. This is how you unit-test data logic without a cluster.

## Gotchas
* NULL in a SQL condition is neither true nor false: use `coalesce(..., false)` so NULL counts as failure.
* Rules reflect business agreements; get them from the data owner, not from guessing.

## Try it yourself
See the notebook. Bonus: add the rule to `quality.py`, run `pytest`, and see which test tells you to update the Python mirror.
