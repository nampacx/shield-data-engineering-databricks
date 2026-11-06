# 01 · Assemble the platform

**Notebook:** [01_assemble_the_platform.ipynb](../notebooks/databricks/01_assemble_the_platform.ipynb) · **Infra:** [infra/](../infra)

## What you build
`azd up` (Bicep) creates the Azure resources. A notebook then creates the Unity Catalog objects.

| Layer | Created by | What |
|---|---|---|
| Azure | `azd up` | Databricks workspace (Premium), ADLS Gen2 storage, access connector, Key Vault, Event Hubs |
| Unity Catalog | you (once, UI/CLI) | **Storage credential** `shield_cred` using the access connector |
| Unity Catalog | notebook 01 | External location `shield_managed`, catalog `shield`, schemas `landing`/`bronze`/`silver`/`gold`/`ops`, managed volumes `staging`/`raw`/`checkpoints` |

## Steps
1. `azd env new shielddev` → `azd env set AZURE_LOCATION swedencentral` → `azd up`.
2. `azd env get-values` and note `DATABRICKS_HOST`, `STORAGE_ACCOUNT_NAME`, `ACCESS_CONNECTOR_ID`.
3. Open the workspace URL. The first user to open it is a workspace admin.
4. Create the storage credential. In **Catalog**, click **+** → **Create a credential**, type *Azure Managed Identity*, name `shield_cred`, *Access Connector ID* = the `ACCESS_CONNECTOR_ID` output. (Menu labels move between releases; existing credentials are listed under **Catalog → Connect → Credentials**.) (CLI alternative: `databricks storage-credentials create --json '{"name":"shield_cred","azure_managed_identity":{"access_connector_id":"<id>"}}'` — unverified here.)
5. Clone this repo as a **Git folder** (Workspace → Create → Git folder) and open notebook 01.
6. Fill the `storage_account` widget and run all. Every statement uses `IF NOT EXISTS`, so re-running is safe.

## Why a catalog needs a managed location
The metastore Azure creates for the region has no storage of its own. The catalog's `MANAGED LOCATION` tells Unity Catalog where managed tables and volumes physically live, and the external location + credential authorise that access. The Bicep template already granted the access connector *Storage Blob Data Contributor* on the account.

## What the notebook does
Four steps with check tables: the external location `shield_managed` on the `uc-managed` container, the catalog `shield` with `MANAGED LOCATION`, the five schemas, and the three managed volumes in `shield.landing`. The setup cell stops early if the widget is empty or the credential does not exist. It also opens with a picture of how credential, location, catalog and volumes fit together.

Everything it creates is a Unity Catalog object; no Azure resource is created or changed. Nothing is cleaned up because every later chapter needs it. The notebook has a commented reset (`DROP CATALOG ... CASCADE`) that deletes all tables and files in `shield`.

## Managed versus external volumes
The three volumes are **managed**: Unity Catalog chooses where the files live (inside the catalog's managed location), and dropping the volume deletes them. An **external** volume points at a folder you name in an external location, and dropping it leaves the files. The `landing` container that `azd` created is unused by the notebook on purpose, for the first mini-project below.

## Gotchas
* The credential needs the `CREATE STORAGE CREDENTIAL` privilege on the metastore; the notebook needs `CREATE EXTERNAL LOCATION` (on the metastore and on the credential) and `CREATE CATALOG`. If it is denied, ask an **account admin** to make you metastore admin (account console → Catalog → your metastore).
* The storage account has shared-key access disabled; everything goes through Entra identities.
* `azd down --purge` removes the Azure resources, but the credential, location and catalog live in the Unity Catalog metastore. Whether they disappear with the workspace is not verified here; drop them yourself for a clean slate.
* Optional file events need two extra roles for the connector (Storage Account Contributor, EventGrid EventSubscription Contributor). Not required for this repo.

## Try it yourself
1. Create an *external* volume on the `landing` container (it needs a second external location and `CREATE EXTERNAL VOLUME`), then compare it with a managed volume: where do the files go, and what happens to them when you drop each volume?
2. Run `DESCRIBE CATALOG EXTENDED shield`, find the managed location, and open that folder in the Azure portal's storage browser. What is in it now, and what appears there after chapter 03? (Unity Catalog chooses opaque folder names on purpose.)
3. Add a `sandbox` schema and grant a colleague `USE SCHEMA` + `CREATE TABLE` on it only (plus `USE CATALOG` on the catalog). Check with `SHOW GRANTS` what they can and cannot do. Bonus: re-run `azd up` and read the `what-if` output to see which parts of the infrastructure are idempotent.
