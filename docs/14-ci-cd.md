# 14 · CI/CD

**Files:** [.github/workflows/ci.yml](../.github/workflows/ci.yml) · [tests/](../tests)

> Status: the `test` job runs plain Python and Spark-free logic; the bundle jobs are **untested** and switched off until you set the repo variable `DATABRICKS_CI=true` and the secrets.

## Concepts
* **CI** (every PR): lint (`ruff`), unit tests (`pytest`), bundle validation. Fast, no production access.
* **CD** (merge to main): deploy the bundle to prod, behind an approval gate.
* **What to unit test in data engineering**: pure functions and rule definitions (here: `quality.py`), transformations on tiny in-memory DataFrames, SQL expressions. What to test with integration runs: the pipeline on a dev workspace with generated data.
* **Test pyramid**: many fast unit tests, a few end-to-end runs.
* **Secrets**: never in the repo. Prefer OIDC federation / a service principal over a personal token.

## Run it locally
```bash
pip install -r requirements.txt
ruff check .
pytest -q
```
To also run the Spark parity test: `pip install pyspark` (needs Java 17).

## Enabling the Databricks jobs
1. Create a service principal and give it access to the workspace and catalog.
2. Add repo secrets `DATABRICKS_HOST` and `DATABRICKS_TOKEN` (or switch to OIDC).
3. Add repo variable `DATABRICKS_CI = true`, and a `production` environment with required reviewers.

## Try it yourself
Add a test that fails when someone adds a rule to `INCIDENT_RULES` without a matching case in `failed_rules`. Then break it on purpose in a PR and watch CI go red.
