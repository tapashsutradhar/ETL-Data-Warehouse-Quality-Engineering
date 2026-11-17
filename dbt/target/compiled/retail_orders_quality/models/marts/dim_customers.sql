select customer_id,
       max(customer_name) as customer_name,
       max(email) as email
from "warehouse"."analytics"."stg_orders"
group by customer_id