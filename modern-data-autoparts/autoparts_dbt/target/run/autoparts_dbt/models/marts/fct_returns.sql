
  
    

  create  table "autoparts_dwh"."analytics"."fct_returns__dbt_tmp"
  
  
    as
  
  (
    

with stg_returns as (
    select * from "autoparts_dwh"."analytics"."stg_returns"
),

stg_sales as (
    select * from "autoparts_dwh"."analytics"."stg_sales"
)

select
    r.return_id,
    r.sale_id,
    r.owner_id,
    r.part_id,
    r.returned_at,
    r.quantity,
    r.refund_amount,
    r.reason,
    r.comment
from stg_returns r
-- Data Integrity: повернення має відповідати існуючому продажу
join stg_sales s on r.sale_id = s.sale_id
  );
  