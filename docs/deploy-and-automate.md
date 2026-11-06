# Deploy and automate

**Files:** [databricks.yml](../databricks.yml) · [resources/](../resources) · [.github/workflows/ci.yml](../.github/workflows/ci.yml) · [tests/](../tests) · [infra/](../infra)

> Status: **drafted, not validated.** The Databricks CLI was not installed when this was written, so `databricks bundle validate` has not been run. Run it first and fix whatever it reports (field names change between CLI versions). The `test` job in CI runs plain Python and Spark-free logic and is the only part exercised locally. The bundle jobs in CI are **untested** and switched off until you set the repo variable `DATABRICKS_CI=true` and the secrets.

This is a guide, not a chapter: there is no notebook, because the work happens in config files and a terminal. Do it after chapter 10, or after the capstone (chapter 14), which deploys as a job.

## Why: nobody clicks in production

By chapter 10 you built a platform and a daily job by hand. That works once. It does not survive a colleague, a second environment or a bad Friday. The fix has three parts, and each answers a different question:

| Question | Answer | Where in this repo |
|---|---|---|
| How do I create the cloud resources repeatably? | Infrastructure as code for the cloud | Bicep + `azd` in [infra/](../infra) (chapter 01) |
| How do I deploy jobs and pipelines to each environment the same way? | Infrastructure as code for the workspace | **Declarative Automation Bundles** (formerly Databricks Asset Bundles): [databricks.yml](../databricks.yml), [resources/](../resources) |
| How do I make sure a change is safe before it reaches production? | Continuous integration and delivery | GitHub Actions: [ci.yml](../.github/workflows/ci.yml) |

```
 code change ─▶ pull request ─▶ CI: ruff, pytest, bundle validate
                                         │ green + approved
                                         ▼
   merge to main ─▶ CD: bundle deploy -t prod  (behind an approval gate)
```

## 1 · Bundles: the workspace as code

A **bundle** is `databricks.yml` plus resource files plus the source they reference, deployed as one unit.

| Concept | What it does | In this repo |
|---|---|---|
| **Resource** | A job, pipeline, dashboard or permission described in YAML | `resources/shield_job.yml` (the daily job of chapter 10 plus the health check of chapter 14), the pipeline of chapter 08 |
| **Target** | An environment (`dev`, `prod`) that overrides settings | `databricks.yml` |
| **`mode: development`** | Prefixes resource names with your user and pauses schedules | the `dev` target |
| **`mode: production`** | Expects a stable deploy path and, normally, a service principal | the `prod` target |
| **Variable** | Keeps environment differences out of the code (`${var.catalog}`) | `databricks.yml` (the `catalog` variable is declared but not used yet) |

Commands: `bundle validate` checks, `bundle deploy` creates or updates, `bundle run` starts, `bundle summary` inspects, `bundle destroy` removes.

Notes on what it deploys here:

* The pipeline lands in `shield_insight_<target>` and writes to schema `pipeline_<target>`, not `pipeline` (see [chapter 08](08-declarative-pipelines.md)).
* Job tasks reference notebooks as `.ipynb` files; that is supported. Serverless compute is the default for jobs.
* `health_check` has no `max_retries` and there are no notifications yet; see [chapter 10](10-maria-hill-schedules.md).

### Steps
1. Install the CLI (`winget install Databricks.DatabricksCLI`) and log in: `databricks auth login --host <DATABRICKS_HOST>`.
2. `databricks bundle validate -t dev`
3. `databricks bundle deploy -t dev`
4. `databricks bundle run shield_daily -t dev` (or `shield_insight` for the pipeline).
5. `databricks bundle destroy -t dev` when done.

## 2 · CI/CD: tests before production

* **CI** (every pull request): lint (`ruff`), unit tests (`pytest`), bundle validation. Fast, no production access.
* **CD** (merge to main): deploy the bundle to prod, behind an approval gate (a `production` environment with required reviewers).
* **What to unit test in data engineering:** pure functions and rule definitions (here: [quality.py](../src/shield_data/quality.py) and its mirror), SQL expressions, transformations on tiny in-memory DataFrames. **What to test with integration runs:** the pipeline on a dev workspace with generated data. Many fast unit tests, a few end-to-end runs: the test pyramid.
* **Secrets:** never in the repo. Prefer OIDC federation or a service principal over a personal token.

### Run the checks locally
```bash
pip install -r requirements.txt
ruff check .
python scripts/check_notebooks.py
pytest -q
```
To also run the Spark parity test: `pip install pyspark` (needs Java 17).

### Enable the Databricks jobs in CI
1. Create a service principal and give it access to the workspace and catalog.
2. Add repo secrets `DATABRICKS_HOST` and `DATABRICKS_TOKEN` (or switch to OIDC).
3. Add repo variable `DATABRICKS_CI = true`, and a `production` environment with required reviewers.

## Not covered yet

* Promotion between more than two environments, and per-environment catalogs (mini-project 1).
* Deploying the cloud layer from CI (`azd` in a pipeline).
* Rollbacks: a bundle deploy is not a transaction.

## Gotchas
* Never edit bundle-managed jobs in the UI; the next deploy overwrites your change.
* Production deploys should use a **service principal**, not a person.
* A green CI run proves the Spark-free logic and the lint, not that the pipeline works. That needs the integration run.

## Try it yourself
1. Add a `staging` target and give prod a different catalog (`shield_prod`) through a target-level variable override.
2. Add a test that fails when someone adds a rule to `INCIDENT_RULES` without a matching case in `failed_rules`. Break it on purpose in a pull request and watch CI go red.
3. Add `max_retries` and an email notification to the `health_check` task, then validate the bundle.
