{{ config(materialized='table') }}

with stg_parts as (
    select * from {{ ref('stg_parts') }}
),

stg_manufacturers as (
    select * from {{ ref('stg_manufacturers') }}
)

select
    p.part_id,
    p.part_name,
    p.category,
    p.price,
    p.is_active,
    p.manufacturer_id,
    m.manufacturer_name,
    m.manufacturer_country
from stg_parts p
left join stg_manufacturers m on p.manufacturer_id = m.manufacturer_id
