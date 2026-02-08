{{config(materialized='table')}}

SELECT 
    DISTINCT city_name
FROM {{ref('int_weather_city')}}