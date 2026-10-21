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
5. Clone this repo as a **Git folder** (Workspace → Create → Git folder) and open notebook 01.
6. Fill the `storage_account` widget and run all.

## Why a catalog needs a managed location
The metastore Azure creates for the region has no storage of its own. The catalog's `MANAGED LOCATION` tells Unity Catalog where managed tables and volumes physically live, and the external location + credential authorise that access. The Bicep template already granted the access connector *Storage Blob Data Contributor* on the account.

## Gotchas
* You need the `CREATE STORAGE CREDENTIAL` privilege. If it is denied, ask an **account admin** to make you metastore admin (account console → Catalog → your metastore).
* The storage account has shared-key access disabled; everything goes through Entra identities.
* Optional file events need two extra roles for the connector (Storage Account Contributor, EventGrid EventSubscription Contributor). Not required for this repo.

## Try it yourself
* Re-run `azd up` and read the output of `what-if` to see what is idempotent.
* Add a tag to every resource in Bicep and re-deploy.
