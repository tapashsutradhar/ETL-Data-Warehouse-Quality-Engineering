# Requirements and guided implementation

## Business scenario

A small online retailer needs confidence that order feeds are complete and correctly represented in reporting tables. The synthetic sample allows repeatable development without credentials or customer data.

## Functional requirements

| ID | Requirement | Evidence |
|---|---|---|
| FR-01 | Ingest delimited source data and enforce a clear schema | Pandas reader and source-contract checks |
| FR-02 | Preserve source rows with batch lineage | DuckDB `raw_orders` |
| FR-03 | Build reporting-ready customer and order tables | DuckDB dimensions/facts and dbt marts |
| FR-04 | Reject invalid keys, values, types, dates and status codes | Negative fixture and failed report |
| FR-05 | Reconcile keys, counts, amounts and references | Python checks and dbt tests |
| FR-06 | Retry a corrected batch without partial writes or duplicates | Transaction rollback and repeat-load tests |
| FR-07 | Produce readable and machine-readable run evidence | `latest.md` and `latest.json` |
| FR-08 | Re-run checks in CI on changes | GitHub Actions workflow |

## Non-functional requirements

- Local-first; no cloud account is required for the normal pipeline or CI.
- Reproducible dependencies are pinned by compatible version ranges in `requirements.txt`.
- No secrets or personal data are committed; all sample records are synthetic.
- Keep transformation SQL and quality rules readable for guided learning.

## Implementation sequence

1. Check Python, Git, PowerShell and available disk; create a virtual environment.
2. Install requirements and run the test suite against isolated temporary DuckDB files.
3. Inspect `data/orders.csv` and its source contract in `pipeline.py`.
4. Run the CLI twice to observe reconciliation and idempotency; inspect the reports.
5. Run dbt debug, seed, and build to inspect staging/mart lineage and tests.
6. Review CI results, then adapt the dbt target/profile and warehouse SQL when a Snowflake account is intentionally introduced.

## Test strategy

Pytest covers a valid first load, repeat-load idempotency, invalid duplicate and blank-key data, transaction rollback and recovery, status and amount negative checks, and report output. dbt adds not-null, uniqueness, accepted-value, relationship, and custom amount assertions. GitHub Actions installs dependencies and runs both test paths on pushes and pull requests.

## Acceptance checks

- First CLI run passes and reports eight input/target orders.
- Second CLI run passes and adds no duplicate orders.
- Invalid fixture fails while fact/dimension tables remain empty; corrected retry passes.
- All Pytest and dbt tests pass from a clean checkout.
- Reports include batch status and individual check details.

The project does not claim measured code coverage or production-scale performance.
