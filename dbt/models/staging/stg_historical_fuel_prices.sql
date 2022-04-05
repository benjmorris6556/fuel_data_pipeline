{{ config(materialized='view') }}

select 
    cast(date as date) as date,
    cast(round(sydney, 1) as numeric) as sydney,
    cast(round(melbourne, 1) as numeric) as melbourne,
    cast(round(brisbane, 1) as numeric) as brisbane,
    cast(round(adelaide, 1) as numeric) as adelaide,
    cast(round(darwin, 1) as numeric) as darwin,
    cast(round(perth, 1) as numeric) as perth,
    cast(round(hobart, 1) as numeric) as hobart,
    cast(round(national_average, 1) as numeric) as national_average,
    cast(date_created as datetime) as date_created
from {{ source('staging','raw_historical_fuel_prices') }}