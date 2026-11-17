# Architecture

```text
Synthetic retail CSV → Pandas source contract checks → DuckDB raw_orders
                                                   ├→ dim_customers
                                                   ├→ fact_orders
                                                   └→ batch_audit
DuckDB marts / dbt models → schema + reconciliation checks → JSON / Markdown report
```

The CLI is an independently runnable ETL path. dbt consumes its bundled seed as a repeatable source for the transformation layer and builds staging and marts into the local DuckDB file. CI tests both paths without cloud credentials.

## Data grain and contracts

`data/orders.csv` contains one order per row with customer attributes and item quantity/unit price. `fact_orders` is one row per order key and calculates order amount to cents. `dim_customers` is one row per customer ID. Raw rows carry their load batch ID; `batch_audit` records each attempt, row counts, status, and failure detail.

Source validation runs before the warehouse transaction: required columns and values, unique order IDs, ISO dates, accepted statuses, positive whole-number quantities, and non-negative prices. Target checks reconcile counts and keys, total amount, and customer references. A bad batch cannot partially modify raw or mart tables.

## Flow

1. Read CSV with Pandas as strings to preserve source values and avoid implicit NA coercion.
2. Validate schema and row-level rules, then normalize dates, statuses and numeric fields.
3. Register the frame with DuckDB; insert raw data and upsert customers inside a transaction.
4. Insert facts by stable order key, reconcile the incoming batch and commit only if all checks pass.
5. Persist an audit status and return a machine-readable result; write reports to the requested output folder.

For cloud migration decisions, see [SNOWFLAKE.md](SNOWFLAKE.md).
