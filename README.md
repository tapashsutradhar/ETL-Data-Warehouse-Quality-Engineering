# DataTrust — ETL & Data Warehouse Quality Engineering

A guided, local-first portfolio project for testing an e-commerce orders pipeline. It uses Python, Pandas, DuckDB, SQL, dbt-duckdb, Pytest, Git and GitHub Actions. All bundled records are synthetic. Snowflake is a documented future migration target and is not needed to run this project.

## What it demonstrates

- CSV contract checks for required values, dates, numeric types, accepted order states and unique order keys.
- Pandas ingestion into a DuckDB raw layer, followed by dimensional customer and fact order tables.
- Batch transactions and idempotent order-key loading, with audit records and rollback on invalid batches.
- Source-to-target count, key, amount and referential-integrity reconciliation.
- Positive and negative Pytest fixtures, JSON/Markdown run reports, and CI checks.
- dbt staging and mart models, source declarations, schema tests and a custom amount assertion.

This learning project uses a compact one-row-per-order feed. It does not claim production readiness, live Snowflake execution, measured coverage, or business impact.

## Windows 11 setup

Prerequisites: Python 3.12, Git, and PowerShell. The bundled CI runs on Python 3.12. VS Code is recommended. (The pipeline itself was also exercised on Python 3.14; use Python 3.12 for dbt.) From the project folder:

```powershell
python --version
git --version
$PSVersionTable.PSVersion
Get-PSDrive C
py -0p
# This checkout includes a local Python 3.12 runtime:
.\.python-runtime\cpython-3.12.16-windows-x86_64-none\python.exe -m venv .venv312
# On a fresh clone with Python 3.12 registered in Windows, use instead:
# py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install --upgrade pip
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "$PWD\src"
```

Use Python 3.12 for dbt. This device had only Python 3.14 registered with the launcher, so this checkout was tested with an isolated project-local Python 3.12 runtime at `.python-runtime` and environment `.venv312`. On a fresh clone, install Python 3.12 or point `py -3.12` at an existing 3.12 installation. Using the virtual environment's Python directly avoids PowerShell activation-policy changes.

## Run the pipeline and tests

```powershell
.\.venv312\Scripts\python.exe -m etl_quality.cli --source data\orders.csv --db .\warehouse.duckdb --report-dir reports
.\.venv312\Scripts\python.exe -m etl_quality.cli --source data\orders.csv --db .\warehouse.duckdb --report-dir reports
.\.venv312\Scripts\python.exe -m pytest -v
```

The first load should accept all eight sample orders; a repeat load should insert zero duplicates. Open `reports\latest.md` or `reports\latest.json` for the check-level results. The negative fixture injects a duplicate key and a blank customer ID, confirms failure without partial fact/dimension writes, then verifies recovery from the valid feed.

## Build the dbt warehouse

```powershell
.\.venv312\Scripts\dbt.exe debug --project-dir dbt --profiles-dir dbt
.\.venv312\Scripts\dbt.exe seed --project-dir dbt --profiles-dir dbt
.\.venv312\Scripts\dbt.exe build --project-dir dbt --profiles-dir dbt
```

dbt-duckdb writes a local `warehouse.duckdb`. The dbt seed is a reproducible source for the transformation layer; the Python CLI independently demonstrates ingestion, batch handling, and operational reconciliation.

## Repository map

```text
data/                 Synthetic e-commerce order feed
src/etl_quality/      Pandas ingestion, DuckDB load, validations and reports
sql/                  DuckDB raw, dimension, fact and audit DDL
dbt/                  DuckDB profile, seed, staging/mart models and tests
tests/                Pytest positive, negative, rollback and report checks
docs/                 Architecture, requirements, quality rules, runbook, migration plan
.github/workflows/    Automated test and dbt build workflow
```

See [architecture](docs/ARCHITECTURE.md), [requirements and implementation plan](docs/IMPLEMENTATION-PLAN.md), [quality rules](docs/QUALITY-RULES.md), [runbook](docs/RUNBOOK.md), and [future Snowflake migration](docs/SNOWFLAKE.md).
