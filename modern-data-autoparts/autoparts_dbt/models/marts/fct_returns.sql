{{ config(materialized='table') }}

with stg_returns as (
    select * from {{ ref('stg_returns') }}
),

stg_sales as (
    select * from {{ ref('stg_sales') }}
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
