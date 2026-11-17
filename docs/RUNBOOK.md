# Local operations runbook

## Run

From the repository root, set `PYTHONPATH` to `src` and use the Python 3.12 virtual environment:

```powershell
.\.venv312\Scripts\python.exe -m etl_quality.cli --source data\orders.csv --db .\warehouse.duckdb --report-dir reports
```

Exit code 0 means all checks passed; 1 means source or warehouse quality failed. The latest JSON and Markdown reports live in `reports/`; audit history is in the DuckDB `batch_audit` table.

## Investigate and recover

1. Read the failed rule and detail in `reports\latest.md`.
2. Locate and correct the source row using the stated key/column issue.
3. Rerun the pipeline. Failed batch writes roll back; a corrected source can be retried against the same local database.
4. Verify a passed status, matching keys/count/amount, and no orphan customer references.

## Reset demo data

Close any process using the local warehouse, then remove the generated database and report files if a clean demo is needed:

```powershell
Remove-Item .\warehouse.duckdb -ErrorAction SilentlyContinue
Remove-Item .\reports\latest.json, .\reports\latest.md -ErrorAction SilentlyContinue
```

These are generated local artifacts and are excluded from Git.
