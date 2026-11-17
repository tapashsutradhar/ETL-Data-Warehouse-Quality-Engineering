# Future Snowflake migration

The supported learning and CI target today is local DuckDB. Snowflake is intentionally not a required dependency and this project has not been run against a Snowflake account.

When migration is desired:

1. Keep the source contract, quality rules and reconciliation expectations unchanged.
2. Add `dbt-snowflake` as an optional adapter and create a separate Snowflake profile driven only by environment variables or a secrets manager.
3. Review DuckDB-specific SQL/data types and replace them with Snowflake-compatible equivalents; validate decimal rounding, date parsing, merge/idempotency behavior and transaction semantics.
4. Run `dbt debug`, then seed/build in a disposable development schema; inspect compiled SQL, warehouse costs and grants.
5. Add CI secrets only after repository permissions and least-privilege roles are reviewed. Never commit account credentials.

The present dbt project uses the `dbt-duckdb` adapter and the local `warehouse.duckdb` file. No cloud deployment, production readiness, or live Snowflake validation is implied.
