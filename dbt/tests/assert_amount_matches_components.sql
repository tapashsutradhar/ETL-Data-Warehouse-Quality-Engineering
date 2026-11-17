select order_id
from {{ ref('fct_orders') }}
where order_amount != round(quantity * unit_price, 2)

