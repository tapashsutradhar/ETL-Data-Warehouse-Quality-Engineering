with source as (
    select * from "warehouse"."analytics"."orders"
), normalized as (
    select
        trim(order_id) as order_id,
        trim(customer_id) as customer_id,
        trim(customer_name) as customer_name,
        lower(trim(email)) as email,
        cast(order_date as date) as order_date,
        lower(trim(status)) as status,
        cast(quantity as integer) as quantity,
        cast(unit_price as decimal(10,2)) as unit_price,
        cast(quantity * unit_price as decimal(12,2)) as order_amount
    from source
)
select * from normalized