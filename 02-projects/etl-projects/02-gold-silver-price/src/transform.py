import logging
from datetime import datetime
import requests
import pandas as pd

def transform_data(**context):
    date_wib = datetime.now()
    raw_data = context['ti'].xcom_pull(key = 'metal_data_raw',task_ids = 'extract_task')
    raw_data["timestamp"] = datetime.fromtimestamp(raw_data["timestamp"])
    
    idr_rate = context['ti'].xcom_pull(key = 'exchange_rate_idr',task_ids = 'extract_task')
    logging.info("Transforming data into structured schema")
    schema = {
        "timestamp": raw_data["timestamp"],
        "metal": raw_data["metal"],
        "currency": raw_data["currency"],
        "exchange":raw_data["exchange"],
        "symbol": raw_data["symbol"],
        "price_usd":raw_data["price"],
        "price_idr": raw_data["price"]*idr_rate,
        "prev_close_price": raw_data["prev_close_price"],
        "open_price": raw_data["open_price"],
        "high_price": raw_data["high_price"],
        "low_price":raw_data["low_price"],
        "ch": raw_data["ch"],
        "chp": raw_data["chp"],
        "ingestion_times": date_wib
    }
    context['ti'].xcom_push(key = 'metal_data_clean',value= schema)
    logging.info("Transformation completed")    