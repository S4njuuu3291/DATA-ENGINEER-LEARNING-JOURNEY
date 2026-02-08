{{config(materialized='view')}}

SELECT 
    city as city_name,
    temp as temperature_c,
    humidity 
FROM {{source('dbt_weather_sanju','weather_daily')}}
WHERE humidity IS NOT NULL