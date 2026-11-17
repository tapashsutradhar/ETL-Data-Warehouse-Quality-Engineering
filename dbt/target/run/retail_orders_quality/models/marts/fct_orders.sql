
  
    
    

    create  table
      "warehouse"."analytics"."fct_orders__dbt_tmp"
  
    as (
      select order_id, customer_id, order_date, status, quantity, unit_price, order_amount
from "warehouse"."analytics"."stg_orders"
    );
  
  