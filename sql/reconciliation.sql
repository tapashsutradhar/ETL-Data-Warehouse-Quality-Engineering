-- DuckDB query template: replace the batch id literal with an audited batch id.
SELECT a.batch_id,
       a.source_rows,
       COUNT(DISTINCT r.order_id) AS unique_source_orders,
       COUNT(DISTINCT f.order_id) AS matched_target_orders,
       ROUND(SUM(r.quantity * r.unit_price), 2) AS source_amount,
       (SELECT ROUND(SUM(f2.order_amount), 2)
          FROM fact_orders f2
         WHERE f2.order_id IN (SELECT order_id FROM raw_orders WHERE batch_id = a.batch_id)) AS target_amount
  FROM batch_audit a
  JOIN raw_orders r ON r.batch_id = a.batch_id
  LEFT JOIN fact_orders f ON f.order_id = r.order_id
 WHERE a.batch_id = 'REPLACE_WITH_BATCH_ID'
 GROUP BY a.batch_id, a.source_rows;
