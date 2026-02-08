{{config(materialized='view')}}

SELECT
    {{ rename_columns({
        'city':'city_name',
        'temp':'temperature_c',
        'humidity': 'humidity_pct'
    })}}
FROM {{source('dbt_weather_sanju','weather_daily')}}