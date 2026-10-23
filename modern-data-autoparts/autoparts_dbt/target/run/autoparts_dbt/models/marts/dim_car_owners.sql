
  
    

  create  table "autoparts_dwh"."analytics"."dim_car_owners__dbt_tmp"
  
  
    as
  
  (
    

select
    owner_id,
    full_name,
    email,
    phone,
    city,
    car_brand,
    car_year,
    registration_date
from "autoparts_dwh"."analytics"."stg_car_owners"
  );
  