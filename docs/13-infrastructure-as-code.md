# 13 · Infrastructure as code

**Files:** [databricks.yml](../databricks.yml) · [resources/](../resources) · [infra/](../infra)

> Status: **drafted, not validated.** The Databricks CLI was not installed when this was written, so `databricks bundle validate` has not been run. Run it first and fix whatever it reports (field names change between CLI versions).

## How to do this chapter

**Before you start:** you have the Databricks CLI, `azd up` has run (chapter 01), and you can open a terminal in the repo folder. This chapter has **no notebook**: you work in a terminal.

**Steps**
1. Check the CLI is installed: `databricks --version`. If not, install it (step 1 under *Steps* below).
2. Log in once with `databricks auth login --host <DATABRICKS_HOST>`. A browser window opens; sign in with the account you use for the workspace.
3. Run `databricks bundle validate -t dev`. Fix whatever it reports before going on (this has not been run yet).
4. Run `databricks bundle deploy -t dev`, then open **Jobs & Pipelines** in the workspace and look for jobs prefixed with your user name.
5. Run `databricks bundle run shield_daily -t dev` and watch it in the UI. When done, run `databricks bundle destroy -t dev`.

**What you should see:** after deploy, a job and a pipeline in the workspace that you did not click together; after destroy, they are gone again.

Deploying in `dev` mode prefixes names with your user and pauses schedules, so it is safe to try. Do not edit these jobs in the UI; the next deploy overwrites your edits.

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
