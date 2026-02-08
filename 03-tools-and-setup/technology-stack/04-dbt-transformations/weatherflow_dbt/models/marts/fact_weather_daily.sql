{{config(materialized='table')}}

SELECT
    city_name,
    avg_temp_c,
    avg_humidity,
    CURRENT_DATE() as report_date
FROM {{ref('int_weather_city')}}
