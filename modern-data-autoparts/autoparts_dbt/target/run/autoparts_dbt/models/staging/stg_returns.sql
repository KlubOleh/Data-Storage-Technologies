
  create view "autoparts_dwh"."analytics"."stg_returns__dbt_tmp"
    
    
  as (
    with source as (
    select * from "autoparts_dwh"."raw"."returns"
)

select
    return_id,
    sale_id,
    owner_id,
    part_id,
    cast(return_date as timestamp) as returned_at,
    quantity,
    cast(refund_amount as numeric(12, 2)) as refund_amount,
    reason,
    -- Обробка пропущених коментарів
    coalesce(comment, 'Коментар відсутній') as comment
from source
  );