select customer_id,
       max(customer_name) as customer_name,
       max(email) as email
from {{ ref('stg_orders') }}
group by customer_id

