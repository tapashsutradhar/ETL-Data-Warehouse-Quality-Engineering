CREATE TABLE IF NOT EXISTS raw_orders (
  batch_id VARCHAR NOT NULL, order_id VARCHAR NOT NULL, customer_id VARCHAR NOT NULL,
  customer_name VARCHAR NOT NULL, email VARCHAR NOT NULL, order_date DATE NOT NULL,
  status VARCHAR NOT NULL, quantity BIGINT NOT NULL, unit_price DECIMAL(12,2) NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_customers (
  customer_id VARCHAR PRIMARY KEY, customer_name VARCHAR NOT NULL, email VARCHAR NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_orders (
  order_id VARCHAR PRIMARY KEY, customer_id VARCHAR NOT NULL, order_date DATE NOT NULL,
  status VARCHAR NOT NULL, quantity BIGINT NOT NULL CHECK(quantity > 0),
  unit_price DECIMAL(12,2) NOT NULL CHECK(unit_price >= 0),
  order_amount DECIMAL(14,2) NOT NULL
);
CREATE TABLE IF NOT EXISTS batch_audit (
  batch_id VARCHAR PRIMARY KEY, started_at VARCHAR NOT NULL, finished_at VARCHAR,
  source_rows BIGINT NOT NULL, inserted_rows BIGINT NOT NULL DEFAULT 0,
  status VARCHAR NOT NULL, error_message VARCHAR
);
