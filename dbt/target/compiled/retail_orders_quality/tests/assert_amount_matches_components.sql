select order_id
from "warehouse"."analytics"."fct_orders"
where order_amount != round(quantity * unit_price, 2)