{{ config(materialized='view') }}

with pivoted_prices as 
(
    select * from 
        (
         select date, location, fuel_price, date_created
         from {{ source('staging', 'raw_daily_fuel_prices') }}
        )
    pivot(
            sum(fuel_price) as fuel_price
            for location in (
                            'Sydney',
                            'Melbourne',
                            'Brisbane',
                            'Adelaide',
                            'Darwin',
                            'Perth',
                            'Hobart'
                            )
        )
)
select 
    cast(date as date) as date,
    cast(round(fuel_price_Sydney, 1) as numeric) as sydney,
    cast(round(fuel_price_Melbourne, 1) as numeric) as melbourne,
    cast(round(fuel_price_Brisbane, 1) as numeric) as brisbane,
    cast(round(fuel_price_Adelaide, 1) as numeric) as adelaide,
    cast(round(fuel_price_Darwin, 1) as numeric) as darwin,
    cast(round(fuel_price_Perth, 1) as numeric) as perth,
    cast(round(fuel_price_Hobart, 1) as numeric) as hobart,
    cast( 
        round(
            (
                fuel_price_Sydney + 
                fuel_price_Melbourne + 
                fuel_price_Brisbane + 
                fuel_price_Adelaide + 
                fuel_price_Darwin + 
                fuel_price_Perth + 
                fuel_price_Hobart
            ) / 7
            , 1) as numeric) as national_average,
    cast(date_created as datetime) as date_created
from pivoted_prices