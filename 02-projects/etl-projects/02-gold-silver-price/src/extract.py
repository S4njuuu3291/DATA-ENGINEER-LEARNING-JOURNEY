import logging
from airflow.hooks.base import BaseHook
import requests

def extract_data(metal, currency, **context):
    ti = context['ti']

    conn = BaseHook.get_connection("metal_api")
    conn_currency = BaseHook.get_connection("exchange_rate_api")

    api_key_metal = conn.extra_dejson.get("api_key") or conn.password
    api_key_fx = conn_currency.extra_dejson.get("api_key") or conn_currency.password

    url = f"{conn.host}/{metal}/{currency}"
    url_currency = f"{conn_currency.host}{api_key_fx}/latest/{currency}"

    logging.info(f"Extracting {metal} prices in {currency}")
    logging.info(f"Metal API URL: {url}")
    logging.info(f"Exchange rate API URL: {url_currency}")

    headers = {
        "x-access-token": api_key_metal,
        "Content-Type": "application/json"
    }

    try:
        raw_data = requests.get(url, headers=headers).json()
        exchange_rate = requests.get(url_currency).json()
    except Exception as e:
        ti.xcom_push(key="metal_data_raw", value=None)
        ti.xcom_push(key="exchange_rate_idr", value=None)
        raise

    if "timestamp" not in raw_data:
        raise ValueError("Invalid metal API response")

    if "conversion_rates" not in exchange_rate:
        raise ValueError("Invalid exchange rate API response")

    ti.xcom_push(key="metal_data_raw", value=raw_data)
    ti.xcom_push(key="exchange_rate_idr", value=exchange_rate["conversion_rates"]["IDR"])