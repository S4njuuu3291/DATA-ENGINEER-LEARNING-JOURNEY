{{config(materialized='view')}}

SELECT
    city_name,
    AVG(temperature_c) as avg_temp_c,
    AVG(humidity) as avg_humidity
FROM {{ref('stg_weather')}}
GROUP BY city_name