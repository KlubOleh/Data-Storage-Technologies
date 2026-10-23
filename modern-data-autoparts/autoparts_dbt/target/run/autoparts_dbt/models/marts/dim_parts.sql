
  
    

  create  table "autoparts_dwh"."analytics"."dim_parts__dbt_tmp"
  
  
    as
  
  (
    

with stg_parts as (
    select * from "autoparts_dwh"."analytics"."stg_parts"
),

stg_manufacturers as (
    select * from "autoparts_dwh"."analytics"."stg_manufacturers"
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
  );
  