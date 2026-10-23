
  
    

  create  table "autoparts_dwh"."analytics"."dim_manufacturers__dbt_tmp"
  
  
    as
  
  (
    

select
    manufacturer_id,
    manufacturer_name,
    manufacturer_country
from "autoparts_dwh"."analytics"."stg_manufacturers"
  );
  