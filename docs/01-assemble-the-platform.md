# 01 · Assemble the platform

**Notebook:** [01_assemble_the_platform.py](../notebooks/databricks/01_assemble_the_platform.py) · **Infra:** [infra/](../infra)

## What you build
`azd up` (Bicep) creates the Azure resources. A notebook then creates the Unity Catalog objects.

| Layer | Created by | What |
|---|---|---|
| Azure | `azd up` | Databricks workspace (Premium), ADLS Gen2 storage, access connector, Key Vault, Event Hubs |
| Unity Catalog | you (once, UI/CLI) | **Storage credential** `shield_cred` using the access connector |
| Unity Catalog | notebook 01 | External location, catalog `shield`, schemas, volumes |

## Steps
1. `azd env new shielddev` → `azd env set AZURE_LOCATION swedencentral` → `azd up`.
2. `azd env get-values` and note `DATABRICKS_HOST`, `STORAGE_ACCOUNT_NAME`, `ACCESS_CONNECTOR_ID`.
3. Open the workspace URL. The first user to open it is a workspace admin.
4. Create the storage credential. **Catalog → Connect → Credentials → Create credential** → type *Azure Managed Identity*, name `shield_cred`, *Access Connector ID* = the `ACCESS_CONNECTOR_ID` output. (CLI alternative: `databricks storage-credentials create --json '{"name":"shield_cred","azure_managed_identity":{"access_connector_id":"<id>"}}'` — unverified here.)
5. Get the repo into the workspace and open notebook 01 (walkthrough below).
6. Run notebook 01 (walkthrough below).

## Walkthrough: open and run notebook 01
New to Databricks notebooks? The generic steps live in [how-to-run-notebooks.md](how-to-run-notebooks.md); this section covers what is special to chapter 01.

### A. Open the notebook
Follow [How to run a chapter notebook](how-to-run-notebooks.md), sections 1 to 3: put the repo in your workspace as a Git folder, open `notebooks/databricks/01_assemble_the_platform`, and connect serverless compute. Then come back here for the part that is special to chapter 01.

### B. Fill the `storage_account` widget
A **widget** is a small input box above the notebook. This notebook has two:

| Widget | Default | What to enter |
|---|---|---|
| `storage_account` | empty | The name of the storage account `azd up` created. **You must fill this in.** |
| `credential` | `shield_cred` | The storage credential from step 4. Leave it unless you named yours differently. |

The boxes **do not exist until the first code cell has run**, because that cell creates them. So the very first time:

1. Run the first code cell (the one starting with `dbutils.widgets.text`) with **Shift+Enter**. It only creates the two boxes; they appear in the widget panel, at the top of the notebook or at this cell.
2. In a terminal in the repo, run `azd env get-values` and copy the value of `STORAGE_ACCOUNT_NAME`. It is a short lowercase name such as `stshielddevabc123`.
3. Paste **only that name** into the `storage_account` box. No `https://`, no `.dfs.core.windows.net`, no path, no spaces. Press Enter.
4. Run the **next** code cell (the one with `assert sa`). It reads the box and passes once it is filled. Then continue with that cell's run menu → **Run All Below**. Avoid **Run all** from the top once the box is filled: it re-runs the cell that creates the widgets, and may reset what you typed.

The creating and the reading are two separate cells on purpose: a cell that creates a widget and immediately demands a value would always fail the first time.

Why the name is needed: the notebook builds `abfss://uc-managed@<storage_account>.dfs.core.windows.net/` from it. That path is the external location and the catalog's managed location, i.e. where the `shield` catalog physically keeps its data.

Still no box? See "No boxes showing?" in [how-to-run-notebooks.md](how-to-run-notebooks.md#5-widgets-input-boxes). The quick fix is **Edit → Add parameter**, name `storage_account`, type *Text*.

### C. Check that it worked
The last two cells print tables. You should see the schemas `landing`, `bronze`, `silver`, `gold`, `ops` and three volumes `staging`, `raw`, `checkpoints`. You can also open **Catalog** in the left sidebar and browse to `shield`.

The notebook is safe to re-run: every statement uses `IF NOT EXISTS`.

### If something fails
* `Fill in the storage_account widget`: the box is empty. Fill it and click **Run all** again.
* An error on `CREATE EXTERNAL LOCATION` mentioning the credential or permissions: `shield_cred` does not exist yet (step 4), the `credential` widget holds a different name, or you lack the privileges listed under Gotchas.
* A "path not found" or host-name error: typo or extra characters in the storage account name. Compare it with the `azd env get-values` output.
* The widget boxes vanished: they reset when the compute session ends. Run the first code cell again and re-enter the name.

## Why a catalog needs a managed location
The metastore Azure creates for the region has no storage of its own. The catalog's `MANAGED LOCATION` tells Unity Catalog where managed tables and volumes physically live, and the external location + credential authorise that access. The Bicep template already granted the access connector *Storage Blob Data Contributor* on the account.

## Gotchas
* You need the `CREATE STORAGE CREDENTIAL` privilege. If it is denied, ask an **account admin** to make you metastore admin (account console → Catalog → your metastore).
* The storage account has shared-key access disabled; everything goes through Entra identities.
* Optional file events need two extra roles for the connector (Storage Account Contributor, EventGrid EventSubscription Contributor). Not required for this repo.

## Try it yourself
* Re-run `azd up` and read the output of `what-if` to see what is idempotent.
* Add a tag to every resource in Bicep and re-deploy.
