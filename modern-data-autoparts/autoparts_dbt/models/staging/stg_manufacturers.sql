with source as (
    select * from {{ source('raw_autoparts', 'manufacturers') }}
)

select
    manufacturer_id,
    manufacturer_name,
    country as manufacturer_country
from source
