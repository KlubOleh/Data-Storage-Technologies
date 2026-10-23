with source as (
    select * from "autoparts_dwh"."raw"."manufacturers"
)

select
    manufacturer_id,
    manufacturer_name,
    country as manufacturer_country
from source