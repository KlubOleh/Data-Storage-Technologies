{{ config(materialized='table') }}

select
    manufacturer_id,
    manufacturer_name,
    manufacturer_country
from {{ ref('stg_manufacturers') }}
