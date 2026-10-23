{{ config(materialized='table') }}

select
    owner_id,
    full_name,
    email,
    phone,
    city,
    car_brand,
    car_year,
    registration_date
from {{ ref('stg_car_owners') }}
