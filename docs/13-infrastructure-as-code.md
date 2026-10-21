# 13 · Infrastructure as code

**Files:** [databricks.yml](../databricks.yml) · [resources/](../resources) · [infra/](../infra)

> Status: **drafted, not validated.** The Databricks CLI was not installed when this was written, so `databricks bundle validate` has not been run. Run it first and fix whatever it reports (field names change between CLI versions).

## Two layers of IaC
| Layer | Tool | Manages |
|---|---|---|
| Cloud | Bicep + `azd` (chapter 01) | Workspace, storage, Key Vault, Event Hubs |
| Workspace | **Declarative Automation Bundles** (formerly Databricks Asset Bundles) | Jobs, pipelines, notebooks, dashboards, permissions |

## Concepts
* A **bundle** = `databricks.yml` + resource files + the source they reference, deployed as one unit.
* **Targets** (`dev`, `prod`) override settings per environment. `mode: development` prefixes resource names with your user and pauses schedules; `mode: production` expects a stable deploy path and (normally) a service principal.
* **Variables** (`${var.catalog}`) keep environment differences out of the code.
* Deploy = `bundle deploy`, run = `bundle run`, inspect = `bundle summary`, remove = `bundle destroy`.

## Steps
1. Install the CLI (`winget install Databricks.DatabricksCLI`) and log in: `databricks auth login --host <DATABRICKS_HOST>`.
2. `databricks bundle validate -t dev`
3. `databricks bundle deploy -t dev`
4. `databricks bundle run shield_daily -t dev` (or `shield_insight` for the pipeline).
5. `databricks bundle destroy -t dev` when done.

## Gotchas
* Never edit bundle-managed jobs in the UI; the next deploy overwrites your change.
* Production deploys should use a **service principal**, not a person.

## Try it yourself
Add a `staging` target; give prod a different catalog (`shield_prod`) through a target-level variable override.
