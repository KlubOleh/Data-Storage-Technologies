with source as (
    select * from "autoparts_dwh"."raw"."sales"
)

select
    sale_id,
    owner_id,
    part_id,
    cast(sale_date as timestamp) as sold_at,
    quantity,
    cast(unit_price as numeric(12, 2)) as unit_price,
    payment_method
from source
where quantity > 0