select order_id, customer_id, order_date, status, quantity, unit_price, order_amount
from {{ ref('stg_orders') }}

