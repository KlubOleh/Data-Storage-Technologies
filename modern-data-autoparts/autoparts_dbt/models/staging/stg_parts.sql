with source as (
    select * from {{ source('raw_autoparts', 'parts') }}
)

select
    part_id,
    manufacturer_id,
    part_name,
    category,
    cast(price as numeric(12, 2)) as price,
    cast(is_active as boolean) as is_active
from source
where price >= 0
