# How to run a chapter notebook (beginner guide)

Every notebook chapter (00–12, 15, 16) is run the same way. Learn it once here; each chapter doc then only lists what is *different*. Menu names shift a little between Databricks releases, so treat the labels as landmarks.

## 0. Words you will meet
| Word | Plain meaning |
|---|---|
| **Workspace** | The Databricks website for your account. Everything below happens in it. |
| **Notebook** | A document made of *cells*. A cell is either text or code. You run code cells one by one or all at once. |
| **Compute** | The machine that actually runs your code. Without it, a notebook is just text. |
| **Serverless** | Compute Databricks starts for you in seconds and stops when idle. The default choice in this repo. |
| **Git folder** | A copy of this GitHub repo inside your workspace, so the files show up as notebooks. |
| **Widget** | A small input box above a notebook. Some notebooks read a value from it. |
| **Catalog Explorer** | The **Catalog** page in the left sidebar. It shows the catalogs, schemas, tables and volumes your notebooks create. |

## 1. Put the repo in your workspace (once)
1. Click **Workspace** in the left sidebar.
2. Expand **Workspace → Users** and right-click your own user folder.
3. Choose **Create → Git folder**.
4. Paste this repo's HTTPS clone URL (`https://github.com/<owner>/<repo>.git`), set **Git provider** to *GitHub*, and click **Create Git folder**.
5. If the repo is private, Databricks first needs your GitHub credentials: your username (top right) → **Settings → Linked accounts** → *Git integration* → GitHub → *Personal access token*.

If the notebooks you expect are missing, you probably cloned a different branch. Click the branch button next to the folder name and switch to the branch the chapters live on. To get later updates, use the same Git dialog and click **Pull** (a pull clears the notebook's state, so re-run it afterwards).

## 2. Open a notebook
1. **Workspace** → your Git folder → `notebooks` → `databricks`.
2. Click the file for your chapter, for example `02_first_recon`. It opens as a notebook: a column of cells.

The notebooks are stored as `.py` files with `# COMMAND ----------` separators. Databricks shows each block as its own cell, so you never need to look at that syntax.

## 3. Connect compute
The compute selector is in the toolbar at the top right of the notebook. It shows the compute's name once connected.
* In a workspace with Unity Catalog, new notebooks default to **serverless** and connect automatically when you run a cell.
* If nothing is connected, click the selector and choose **Serverless** (or a running cluster).
* Chapter 09 part B may need classic compute instead; its doc says so.

## 4. Run it
* **Run one cell:** click inside it and press **Shift+Enter** (it runs, then moves to the next cell). The right-arrow at the cell's top left does the same.
* **Run everything:** click **Run all** in the toolbar. On current runtimes the cells run as a batch and the first error stops the run.
* **Stop:** click the interrupt button in the toolbar.
* **Start over cleanly:** **Run → Clear state and outputs**, then **Run all**.

Two habits that save beginners a lot of grief:
1. **Run top to bottom, in order.** Later cells use variables and tables defined earlier. If you skip a cell you get `NameError` or "table not found".
2. **Read the result under each cell** before running the next one. The chapters teach by what you *see* there.

## 5. Widgets (input boxes)
Widgets appear in a **widget panel**. Depending on your workspace version and settings, the panel sits under the toolbar at the top of the notebook or right at the cell that created them (inside or just below it). It is the same panel either way. Widgets exist **only after the cell that creates them has run**. So the first time:
1. Run the cell that contains `dbutils.widgets...` (Shift+Enter). The boxes appear.
2. Type or choose a value, press Enter.
3. Run the rest, or click **Run all**.

**No boxes showing?** Work through this list:
1. **Did the creating cell run successfully?** It needs a green check or a finished state, not an error. Widgets created in a cell that failed before the `dbutils.widgets` line, or a cell you only clicked but did not run, do not exist.
2. **Is compute connected?** Creating widgets in code needs a notebook attached to compute; with nothing attached the cell cannot run.
3. **Look for the widget panel**: at the top of the notebook, or at the cell that created the widgets. The panel has a gear icon (settings) and a pin icon; pinning places the widgets at the top of the notebook so they stay in one place, and the setting is saved per user.
4. **Create the box by hand.** In the notebook menu choose **Edit → Add parameter**, set *Parameter Name* to exactly the name the notebook uses (for chapter 01: `storage_account`), type *Text*, and save. The code reads it with `dbutils.widgets.get`, so a box made this way works just as well.

Widget values reset when the compute session ends; re-run the creating cell and re-enter them. Chapters that use widgets: 01 (`storage_account`), 09 (`eventhub_namespace`), 10 (`step`, `deliver_files`).

## 6. Look at what you built
Open **Catalog** in the left sidebar → `shield` → a schema (`landing`, `bronze`, `silver`, `gold`, `ops`) → a table or volume. Click a table to see its columns, a sample, and, under **Lineage**, where it came from.

## 7. What to do when something fails
1. Read the **last line** of the red error; it is usually the useful one.
2. Check you ran the cells above it and that the **previous chapters** this one needs have been run (each chapter doc lists them under "Before you start").
3. Look the message up in [troubleshooting](troubleshooting.md).
4. Most notebooks are safe to re-run (they overwrite or use `IF NOT EXISTS`). Where a chapter is **not** safe to re-run, its doc says so.

## 8. Keep the bill small
Serverless stops by itself when idle. Still, finish a session by closing notebooks you are not using, and run `azd down --purge` when you pause the project for a longer time. See the cost warning in [chapter 00](00-briefing-room.md).

## Chapter order and what each needs
The chapters share tables, so order matters:

```
01 platform ─► 02 generate data ─► 03 bronze ─► 04 silver.agents ─► 05 silver/gold ─► 06 quality ─► 07 time travel
                                         │                 │                                  │
                                         │                 └─► 11 governance                  └─► 10 job, 15 ML, 16 health check
                                         └─► 08 pipeline, 09 streaming (needs 02's pings)
12 performance needs 05's silver.locations.   13 and 14 are terminal/GitHub work, no notebook.
```
