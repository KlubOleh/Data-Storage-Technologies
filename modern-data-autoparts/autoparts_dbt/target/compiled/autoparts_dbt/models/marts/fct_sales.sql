

with stg_sales as (
    select * from "autoparts_dwh"."analytics"."stg_sales"
),

stg_car_owners as (
    select * from "autoparts_dwh"."analytics"."stg_car_owners"
),

stg_parts as (
    select * from "autoparts_dwh"."analytics"."stg_parts"
)

select
    s.sale_id,
    s.owner_id,
    s.part_id,
    p.manufacturer_id,
    s.sold_at,
    s.quantity,
    s.unit_price,
    -- Сума продажу = кількість * ціна на момент продажу
    s.quantity * s.unit_price as total_amount,
    s.payment_method
from stg_sales s
-- Data Integrity: беремо лише продажі з існуючими власниками та запчастинами
join stg_car_owners o on s.owner_id = o.owner_id
join stg_parts p on s.part_id = p.part_id