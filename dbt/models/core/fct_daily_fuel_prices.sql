{{
    config(materialized='table')
}}

WITH union_tbl AS (
    SELECT date, sydney, melbourne, brisbane, adelaide, darwin, perth, hobart, national_average, date_created 
    FROM {{ ref('stg_historical_fuel_prices') }}
    UNION ALL
    SELECT date, sydney, melbourne, brisbane, adelaide, darwin, perth, hobart, national_average, date_created
    FROM {{ ref('stg_daily_fuel_prices') }}
    ORDER BY date DESC
),

dates_ranked AS (
    SELECT date, sydney, melbourne, brisbane, adelaide, darwin, perth, hobart, national_average, date_created, RANK() OVER (PARTITION BY date_created ORDER BY date_created DESC) AS rank
    FROM union_tbl
)

SELECT date, sydney, melbourne, brisbane, adelaide, darwin, perth, hobart, national_average, date_created
FROM dates_ranked
WHERE rank = 1
ORDER BY date DESC