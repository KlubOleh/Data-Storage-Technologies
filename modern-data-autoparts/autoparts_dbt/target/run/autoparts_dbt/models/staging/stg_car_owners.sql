
  create view "autoparts_dwh"."analytics"."stg_car_owners__dbt_tmp"
    
    
  as (
    with source as (
    select * from "autoparts_dwh"."raw"."car_owners"
),

-- У raw-шарі є дублікати власників: залишаємо по одному рядку на owner_id
deduplicated as (
    select
        *,
        row_number() over (
            partition by owner_id
            order by registration_date desc
        ) as row_num
    from source
),

renamed_and_cleaned as (
    select
        owner_id,
        full_name,
        -- Обробка пропущених email-ів
        coalesce(email, 'unknown@example.com') as email,
        phone,
        city,
        car_brand,
        cast(car_year as integer) as car_year,
        cast(registration_date as date) as registration_date
    from deduplicated
    where row_num = 1
)

select * from renamed_and_cleaned
  );